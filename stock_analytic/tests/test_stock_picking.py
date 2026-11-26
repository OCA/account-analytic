# Copyright 2013 Julius Network Solutions
# Copyright 2015 Clear Corp
# Copyright 2016 OpenSynergy Indonesia
# Copyright 2017 ForgeFlow S.L.
# Copyright 2018 Hibou Corp.
# Copyright 2023 Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import Command, fields
from odoo.exceptions import ValidationError

from .common import CommonStockPicking


class TestStockPicking(CommonStockPicking):
    _test_user_groups = (
        "base.group_user",
        "stock.group_stock_manager",
        "analytic.group_analytic_accounting",
        "product.group_product_manager",
    )

    def test_outgoing_picking_with_analytic(self):
        picking = self._create_picking(
            self.location,
            self.dest_location,
            self.outgoing_picking_type,
            self.analytic_distribution,
        )
        self._update_qty_on_hand_product(self.product, 1)
        self._confirm_picking_no_error(picking)
        self._picking_done_no_error(picking)
        self._check_account_move_no_error(picking)
        self._check_analytic_account_no_error(picking)
        self._check_analytic_consistency(picking)

    def test_outgoing_picking_without_analytic_optional(self):
        # Create a general optional applicability for stock moves.
        self._create_analytic_applicability()
        # Create a another applicability which makes the analytic mandatory only for
        # incoming stock moves. i.e. applicability should be optional for the outgoing
        applicability_specific = self._create_analytic_applicability()
        applicability_specific.write(
            {
                "stock_picking_type_id": self.incoming_picking_type.id,
                "applicability": "mandatory",
            }
        )
        picking = self._create_picking(
            self.location,
            self.dest_location,
            self.outgoing_picking_type,
        )
        self._update_qty_on_hand_product(self.product, 1)
        self._confirm_picking_no_error(picking)
        self._picking_done_no_error(picking)
        self._check_account_move_no_error(picking)
        self._check_no_analytic_account(picking)
        self._check_analytic_consistency(picking)

    def test_outgoing_picking_without_analytic_mandatory(self):
        # Create a general mandatory applicability for stock moves.
        applicability_general = self._create_analytic_applicability()
        applicability_general.write({"applicability": "mandatory"})
        # Create a another applicability which makes the analytic optional only for
        # incoming stock moves.
        applicability_specific = self._create_analytic_applicability()
        applicability_specific.write(
            {"stock_picking_type_id": self.incoming_picking_type.id}
        )
        picking = self._create_picking(
            self.location,
            self.dest_location,
            self.outgoing_picking_type,
        )
        self._update_qty_on_hand_product(self.product, 1)
        self._confirm_picking_no_error(picking)
        with self.assertRaises(ValidationError):
            self._picking_done_no_error(picking)

    def test_incoming_picking_with_analytic(self):
        picking = self._create_picking(
            self.location,
            self.dest_location,
            self.incoming_picking_type,
            self.analytic_distribution,
        )
        self._update_qty_on_hand_product(self.product, 1)
        self._confirm_picking_no_error(picking)
        self._picking_done_no_error(picking)
        self._check_account_move_no_error(picking)
        self._check_analytic_account_no_error(picking)
        self._check_analytic_consistency(picking)

    def test_picking_add_extra_move_line(self):
        picking = self._create_picking(
            self.location,
            self.dest_location,
            self.outgoing_picking_type,
            self.analytic_distribution,
        )
        move_before = picking.move_ids

        self.env["stock.move.line"].create(
            {
                "product_id": self.product_2.id,
                "location_id": self.location.id,
                "location_dest_id": self.dest_location.id,
                "date": fields.Datetime.now(),
                "uom_id": self.product_2.uom_id.id,
                "analytic_distribution": self.analytic_distribution,
                "company_id": self.env.company.id,
                "picking_id": picking.id,
            }
        )

        move_after = picking.move_ids - move_before

        self.assertEqual(self.analytic_distribution, move_after.analytic_distribution)

    def _replace_default_mto_route(self):
        """
        Set a new MTO route on the product.

        If the tests of this module are run in a database that will also install
        mrp (such as when also testing mrp_stock_analytic), the mrp module will
        change the stock settings so that the default stock routes stop working.
        So we make our own MTO route that will work regardless of whether mrp is
        loaded alongside this module or not.
        """
        src_location = self.location.copy(
            {
                "location_id": self.location.id,
                "name": "Test location",
            }
        )
        dst_location = self.dest_location.copy(
            {
                "location_id": self.dest_location.id,
                "name": "Test location",
            }
        )
        test_route = self.env["stock.route"].create(
            {
                "name": "Test route",
                "product_selectable": True,
                "rule_ids": [
                    Command.create(
                        {
                            "name": f"Pull MTO {src_location.display_name} "
                            f"-> {dst_location.display_name}",
                            "action": "pull",
                            "picking_type_id": self.outgoing_picking_type.id,
                            "location_src_id": src_location.id,
                            "location_dest_id": dst_location.id,
                            "procure_method": "make_to_order",
                        }
                    ),
                    Command.create(
                        {
                            "name": f"Pull MTO {self.location.display_name} "
                            f"-> {src_location.display_name}",
                            "action": "pull",
                            "picking_type_id": self.outgoing_picking_type.id,
                            "location_src_id": self.location.id,
                            "location_dest_id": src_location.id,
                            "procure_method": "make_to_stock",
                        }
                    ),
                ],
            }
        )
        self.product.route_ids = [
            Command.clear(),
            Command.link(test_route.id),
        ]
        return src_location, dst_location

    def test_procurement_with_analytic(self):
        src_location, dst_location = self._replace_default_mto_route()
        picking = self._create_picking(
            src_location,
            dst_location,
            self.outgoing_picking_type,
            self.analytic_distribution,
            procure_method="make_to_order",
        )
        picking.action_confirm()
        procured_moves = picking.move_ids.move_orig_ids
        self.assertTrue(procured_moves)
        for move in procured_moves:
            self.assertEqual(
                move.analytic_distribution,
                self.analytic_distribution,
                msg="In MTO procurement, the analytic distribution should propagate",
            )

    def test_procurement_without_analytic(self):
        src_location, dst_location = self._replace_default_mto_route()
        picking = self._create_picking(
            src_location,
            dst_location,
            self.outgoing_picking_type,
            analytic_distribution=False,
            procure_method="make_to_order",
        )
        picking.action_confirm()
        procured_moves = picking.move_ids.move_orig_ids
        self.assertTrue(procured_moves)
        for move in procured_moves:
            self.assertFalse(move.analytic_distribution)

    def test_outgoing_picking_with_analytic_company_valuation_account(self):
        # The stock valuation account can come from the company instead of the
        # product category; that line must not get the analytic distribution.
        self.product_categ.property_stock_valuation_account_id = False
        self.company.sudo().account_stock_valuation_id = self.valuation_account
        self.env.cr.cache.pop("account_product_accounts", None)
        picking = self._create_picking(
            self.location,
            self.dest_location,
            self.outgoing_picking_type,
            self.analytic_distribution,
        )
        self._update_qty_on_hand_product(self.product, 1)
        self._confirm_picking_no_error(picking)
        self._picking_done_no_error(picking)
        self._check_account_move_no_error(picking)
        self.assertIn(
            self.valuation_account,
            picking.move_ids.account_move_id.sudo().line_ids.account_id,
        )
        self._check_analytic_account_no_error(picking)

    def test_moves_with_different_analytic_are_not_merged(self):
        analytic_account_2 = self.env["account.analytic.account"].create(
            {"name": "Test Analytic Account 2", "plan_id": self.analytic_plan.id}
        )
        analytic_distribution_2 = {str(analytic_account_2.id): 100.0}
        picking = self._create_picking(
            self.location,
            self.dest_location,
            self.outgoing_picking_type,
            self.analytic_distribution,
        )
        picking.action_confirm()
        new_move = picking.move_ids.copy(
            {
                "picking_id": picking.id,
                "product_uom_qty": 2.0,
                "date_deadline": picking.move_ids.date_deadline,
                "analytic_distribution": analytic_distribution_2,
            }
        )
        new_move._action_confirm()
        self.assertEqual(len(picking.move_ids), 2)
        self.assertEqual(
            sorted(picking.move_ids.mapped("product_uom_qty")),
            [1.0, 2.0],
        )

    def test_moves_with_same_analytic_are_merged(self):
        picking = self._create_picking(
            self.location,
            self.dest_location,
            self.outgoing_picking_type,
            self.analytic_distribution,
        )
        picking.action_confirm()
        new_move = picking.move_ids.copy(
            {
                "picking_id": picking.id,
                "product_uom_qty": 2.0,
                "date_deadline": picking.move_ids.date_deadline,
                "analytic_distribution": dict(self.analytic_distribution),
            }
        )
        new_move._action_confirm()
        self.assertEqual(len(picking.move_ids), 1)
        self.assertEqual(picking.move_ids.product_uom_qty, 3.0)
        self.assertEqual(
            picking.move_ids.analytic_distribution, self.analytic_distribution
        )
