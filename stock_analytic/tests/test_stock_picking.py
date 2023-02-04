# Copyright 2013 Julius Network Solutions
# Copyright 2015 Clear Corp
# Copyright 2016 OpenSynergy Indonesia
# Copyright 2017 ForgeFlow S.L.
# Copyright 2018 Hibou Corp.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from datetime import datetime

from odoo.tests.common import TransactionCase


class TestStockPicking(TransactionCase):
    def setUp(self):
        super().setUp()
        self.product = self.env["product.product"].create(
            {
                "name": "Test Product",
                "type": "product",
                "standard_price": 1.0,
            }
        )
        self.product_2 = self.env.ref("product.product_product_5")
        self.product_categ = self.env.ref("product.product_category_5")
        self.valuation_account = self.env["account.account"].create(
            {
                "name": "Test stock valuation",
                "code": "tv",
                "account_type": "liability_current",
                "reconcile": True,
                "company_id": self.env.ref("base.main_company").id,
            }
        )
        self.stock_input_account = self.env["account.account"].create(
            {
                "name": "Test stock input",
                "code": "tsti",
                "account_type": "expense",
                "reconcile": True,
                "company_id": self.env.ref("base.main_company").id,
            }
        )
        self.stock_output_account = self.env["account.account"].create(
            {
                "name": "Test stock output",
                "code": "tout",
                "account_type": "income",
                "reconcile": True,
                "company_id": self.env.ref("base.main_company").id,
            }
        )
        self.stock_journal = self.env["account.journal"].create(
            {"name": "Stock Journal", "code": "STJTEST", "type": "general"}
        )
        self.analytic_distribution = dict(
            {str(self.env.ref("analytic.analytic_agrolait").id): 100.0}
        )
        self.warehouse = self.env.ref("stock.warehouse0")
        self.location = self.warehouse.lot_stock_id
        self.dest_location = self.env.ref("stock.stock_location_customers")
        self.outgoing_picking_type = self.env.ref("stock.picking_type_out")
        self.incoming_picking_type = self.env.ref("stock.picking_type_in")

        self.product_categ.update(
            {
                "property_valuation": "real_time",
                "property_stock_valuation_account_id": self.valuation_account.id,
                "property_stock_account_input_categ_id": self.stock_input_account.id,
                "property_stock_account_output_categ_id": self.stock_output_account.id,
                "property_stock_journal": self.stock_journal.id,
            }
        )
        self.product.update({"categ_id": self.product_categ.id})

    def _create_picking(
        self,
        location_id,
        location_dest_id,
        picking_type_id,
        analytic_distribution=False,
    ):
        picking_data = {
            "picking_type_id": picking_type_id.id,
            "move_type": "direct",
            "location_id": location_id.id,
            "location_dest_id": location_dest_id.id,
        }

        picking = self.env["stock.picking"].create(picking_data)

        move_data = {
            "picking_id": picking.id,
            "product_id": self.product.id,
            "location_id": location_id.id,
            "location_dest_id": location_dest_id.id,
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "date_deadline": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "name": self.product.name,
            "procure_method": "make_to_stock",
            "product_uom": self.product.uom_id.id,
            "product_uom_qty": 1.0,
            "analytic_distribution": analytic_distribution or False,
        }

        self.env["stock.move"].create(move_data)

        return picking

    def __update_qty_on_hand_product(self, product, new_qty):
        self.env["stock.quant"]._update_available_quantity(
            product, self.location, new_qty
        )

    def _confirm_picking_no_error(self, picking):
        picking.action_confirm()
        self.assertEqual(picking.state, "assigned")

    def _picking_done_no_error(self, picking):
        picking.move_ids.quantity_done = 1.0
        picking.button_validate()
        self.assertEqual(picking.state, "done")

    def _check_account_move_no_error(self, picking):
        criteria1 = [
            ["ref", "=", "{} - {}".format(picking.name, picking.product_id.name)]
        ]
        acc_moves = self.env["account.move"].search(criteria1)
        self.assertTrue(len(acc_moves) > 0)

    def _check_analytic_account_no_error(self, picking):
        move = picking.move_ids[0]
        criteria2 = [["move_id.ref", "=", picking.name]]
        acc_lines = self.env["account.move.line"].search(criteria2)
        for acc_line in acc_lines:
            if (
                acc_line.account_id
                != move.product_id.categ_id.property_stock_valuation_account_id
            ):
                self.assertEqual(
                    acc_line.analytic_distribution, move.analytic_distribution
                )

    def _check_no_analytic_account(self, picking):
        criteria2 = [
            ("move_id.ref", "=", picking.name),
            ("analytic_distribution", "!=", False),
        ]
        line_count = self.env["account.move.line"].search_count(criteria2)
        self.assertEqual(line_count, 0)

    def test_outgoing_picking_with_analytic(self):
        picking = self._create_picking(
            self.location,
            self.dest_location,
            self.outgoing_picking_type,
            self.analytic_distribution,
        )
        self.__update_qty_on_hand_product(self.product, 1)
        self._confirm_picking_no_error(picking)
        self._picking_done_no_error(picking)
        self._check_account_move_no_error(picking)
        self._check_analytic_account_no_error(picking)

    def test_outgoing_picking_without_analytic(self):
        picking = self._create_picking(
            self.location,
            self.dest_location,
            self.outgoing_picking_type,
        )
        self.__update_qty_on_hand_product(self.product, 1)
        self._confirm_picking_no_error(picking)
        self._picking_done_no_error(picking)
        self._check_account_move_no_error(picking)
        self._check_no_analytic_account(picking)

    def test_incoming_picking_with_analytic(self):
        picking = self._create_picking(
            self.location,
            self.dest_location,
            self.incoming_picking_type,
            self.analytic_distribution,
        )
        self.__update_qty_on_hand_product(self.product, 1)
        self._confirm_picking_no_error(picking)
        self._picking_done_no_error(picking)
        self._check_account_move_no_error(picking)
        self._check_analytic_account_no_error(picking)

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
                "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "product_uom_id": self.product_2.uom_id.id,
                "reserved_uom_qty": 1.0,
                "analytic_distribution": self.analytic_distribution,
                "company_id": self.env.company.id,
                "picking_id": picking.id,
            }
        )

        move_after = picking.move_ids - move_before

        self.assertEqual(self.analytic_distribution, move_after.analytic_distribution)

    def test__prepare_procurement_values(self):
        picking = self._create_picking(
            self.location,
            self.dest_location,
            self.outgoing_picking_type,
            self.analytic_distribution,
        )
        values = picking.move_ids._prepare_procurement_values()
        self.assertEqual(self.analytic_distribution, values["analytic_distribution"])
        picking = self._create_picking(
            self.location,
            self.dest_location,
            self.outgoing_picking_type,
        )
        values = picking.move_ids._prepare_procurement_values()
        self.assertEqual(values.get("analytic_distribution"), None)
