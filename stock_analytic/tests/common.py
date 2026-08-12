# Copyright 2013 Julius Network Solutions
# Copyright 2015 Clear Corp
# Copyright 2016 OpenSynergy Indonesia
# Copyright 2017 ForgeFlow S.L.
# Copyright 2018 Hibou Corp.
# Copyright 2023 Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from datetime import datetime

from odoo import Command

from odoo.addons.base.tests.common import BaseCommon


class CommonStockPicking(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product = cls.env["product.product"].create(
            {
                "name": "Test Product",
                "type": "consu",
                "is_storable": True,
                "standard_price": 1.0,
            }
        )
        cls.product_2 = cls.env["product.product"].create(
            {
                "name": "Test Product 2",
                "type": "consu",
                "is_storable": True,
            }
        )
        cls.product_categ = cls.env["product.category"].create(
            {"name": "Test Category"}
        )
        cls.valuation_account = cls.env["account.account"].create(
            {
                "name": "Test stock valuation",
                "code": "tv",
                "account_type": "liability_current",
                "reconcile": True,
                "company_ids": [Command.link(cls.company.id)],
            }
        )
        cls.stock_output_account = cls.env["account.account"].create(
            {
                "name": "Test stock output",
                "code": "tout",
                "account_type": "expense",
                "company_ids": [Command.link(cls.company.id)],
            }
        )
        cls.stock_journal = cls.env["account.journal"].create(
            {
                "name": "Stock Journal",
                "code": "STJTEST",
                "type": "general",
                "company_id": cls.company.id,
            }
        )
        # Odoo 19 stock_account uses company.account_stock_journal_id for valuation
        # entries (not only category.property_stock_journal).
        cls.company.write({"account_stock_journal_id": cls.stock_journal.id})
        cls.analytic_plan = cls.env["account.analytic.plan"].create(
            {"name": "Test Plan"}
        )
        cls.analytic_account = cls.env["account.analytic.account"].create(
            {"name": "Test Analytic Account", "plan_id": cls.analytic_plan.id}
        )
        cls.analytic_distribution = {str(cls.analytic_account.id): 100.0}
        cls.warehouse = cls.env.ref("stock.warehouse0")
        cls.location = cls.warehouse.lot_stock_id
        cls.dest_location = cls.env.ref("stock.stock_location_customers")
        cls.dest_location.valuation_account_id = cls.stock_output_account.id
        cls.outgoing_picking_type = cls.env.ref("stock.picking_type_out")
        cls.incoming_picking_type = cls.env.ref("stock.picking_type_in")

        cls.product_categ.update(
            {
                "property_valuation": "real_time",
                "property_stock_valuation_account_id": cls.valuation_account.id,
                "property_stock_journal": cls.stock_journal.id,
            }
        )
        cls.product.update({"categ_id": cls.product_categ.id})

    def _create_analytic_applicability(self):
        return self.env["account.analytic.applicability"].create(
            {
                "business_domain": "stock_move",
                "applicability": "optional",
                "analytic_plan_id": self.analytic_plan.id,
            }
        )

    def _create_picking(
        self,
        location_id,
        location_dest_id,
        picking_type_id,
        analytic_distribution=False,
        procure_method="make_to_stock",
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
            "procure_method": procure_method,
            "product_uom": self.product.uom_id.id,
            "product_uom_qty": 1.0,
            "analytic_distribution": analytic_distribution or False,
        }

        self.env["stock.move"].create(move_data)

        return picking

    def _update_qty_on_hand_product(self, product, new_qty):
        self.env["stock.quant"]._update_available_quantity(
            product, self.location, new_qty
        )

    def _confirm_picking_no_error(self, picking):
        picking.action_confirm()
        self.assertEqual(picking.state, "assigned")

    def _picking_done_no_error(self, picking):
        picking.move_ids.quantity = 1.0
        picking.button_validate()
        self.assertEqual(picking.state, "done")

    def _check_account_move_no_error(self, picking):
        acc_moves = picking.move_ids.mapped("account_move_id")
        self.assertTrue(len(acc_moves) > 0)

    def _check_analytic_account_no_error(self, picking):
        move = picking.move_ids[0]
        acc_lines = move.account_move_id.line_ids
        for acc_line in acc_lines:
            if acc_line.account_id == self.valuation_account:
                self.assertEqual(acc_line.analytic_distribution, False)
            else:
                self.assertEqual(
                    acc_line.analytic_distribution, move.analytic_distribution
                )

    def _check_no_analytic_account(self, picking):
        acc_lines = picking.move_ids.mapped("account_move_id").mapped("line_ids")
        analytic_lines = acc_lines.filtered(lambda line: line.analytic_distribution)
        self.assertEqual(len(analytic_lines), 0)

    def _check_analytic_consistency(self, picking):
        for move_line in picking.move_line_ids:
            self.assertEqual(
                move_line.analytic_distribution, move_line.move_id.analytic_distribution
            )
