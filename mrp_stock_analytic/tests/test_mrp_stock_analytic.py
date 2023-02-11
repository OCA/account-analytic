# Copyright 2023 Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import Form

from odoo.addons.stock_analytic.tests.test_stock_picking import TestStockPicking


class TestMrpStockAnalytic(TestStockPicking):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.stock_location_id = cls.env["ir.model.data"]._xmlid_to_res_id(
            "stock.stock_location_stock"
        )
        cls.product_A = cls.env["product.product"].create(
            {
                "name": "Product A",
                "type": "product",
                "categ_id": cls.product_categ.id,
                "standard_price": 10.0,
            }
        )
        cls.product_B = cls.env["product.product"].create(
            {
                "name": "Product B",
                "type": "product",
                "categ_id": cls.product_categ.id,
                "standard_price": 10.0,
            }
        )
        cls.bom = cls.env["mrp.bom"].create(
            {
                "product_id": cls.product_A.id,
                "product_tmpl_id": cls.product_A.product_tmpl_id.id,
                "product_qty": 1.0,
                "bom_line_ids": [
                    (0, 0, {"product_id": cls.product_B.id, "product_qty": 1}),
                ],
            }
        )
        quants = (
            cls.env["stock.quant"]
            .with_context(inventory_mode=True)
            .create(
                {
                    "product_id": cls.product_B.id,
                    "inventory_quantity": 10,
                    "location_id": cls.stock_location_id,
                }
            )
        )
        quants.action_apply_inventory()
        production = cls.env["mrp.production"].create(
            {
                "product_id": cls.product_A.id,
                "bom_id": cls.bom.id,
                "product_qty": 1,
                "product_uom_id": cls.product_A.uom_id.id,
            }
        )
        production.action_confirm()
        mo_form = Form(production)
        mo_form.qty_producing = 1
        cls.production = mo_form.save()

    def test_propagate_analytic_distribution(self):
        production = self.production
        self.assertEqual(len(production.move_raw_ids), 1)
        self.assertEqual(production.analytic_distribution, False)
        self.assertEqual(production.move_raw_ids[0].analytic_distribution, False)
        # Assign analytic distribution and it's propagated to component stock moves.
        production.analytic_distribution = self.analytic_distribution
        self.assertNotEqual(production.analytic_distribution, False)
        self.assertEqual(
            production.move_raw_ids[0].analytic_distribution,
            self.analytic_distribution,
        )
        # Remove analytic distribution and it's propagated to component stock moves.
        production.analytic_distribution = False
        self.assertEqual(production.move_raw_ids[0].analytic_distribution, False)

    def test_analytic_distribution_journal_items(self):
        production = self.production
        production.analytic_distribution = self.analytic_distribution
        self.assertNotEqual(production.analytic_distribution, False)
        production.button_mark_done()
        product_A_move_lines = (
            self.env["account.move"]
            .search([("stock_move_id", "=", production.move_finished_ids.id)])
            .line_ids
        )
        self.assertEqual(len(product_A_move_lines), 2)
        for move_line in product_A_move_lines:
            # No analytic distribution for journal items of the produced product.
            self.assertEqual(move_line.analytic_distribution, False)
        product_B_move_lines = (
            self.env["account.move"]
            .search([("stock_move_id", "=", production.move_raw_ids.id)])
            .line_ids
        )
        self.assertEqual(len(product_B_move_lines), 2)
        for move_line in product_B_move_lines:
            if move_line.account_id == self.valuation_account:
                self.assertEqual(move_line.analytic_distribution, False)
            else:
                self.assertEqual(
                    move_line.analytic_distribution, self.analytic_distribution
                )
