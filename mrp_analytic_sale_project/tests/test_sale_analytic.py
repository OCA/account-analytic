from odoo.tests import common


class TestSaleAnalytic(common.TransactionCase):
    def setUp(self):
        super().setUp()

        mfg_route = self.env.ref("mrp.route_warehouse0_manufacture")
        mto_route = self.env.ref("stock.route_warehouse0_mto")
        mto_route.active = True
        self.default_plan = self.env["account.analytic.plan"].create(
            {"name": "Default", "company_id": False}
        )
        self.analytic_account = self.env["account.analytic.account"].create(
            {
                "name": "Analytic account test",
                "plan_id": self.default_plan.id,
                "company_id": False,
            }
        )

        self.product_service = self.env["product.product"].create(
            {
                "name": "Service",
                "type": "service",
            }
        )
        self.product_stock = self.env["product.product"].create(
            {
                "name": "Storable",
                "type": "product",
                "route_ids": [(6, 0, [mfg_route.id, mto_route.id])],
            }
        )
        self.bom_product_stock = self.env["mrp.bom"].create(
            {"product_tmpl_id": self.product_stock.product_tmpl_id.id}
        )

    def test_100_sale_analytic_to_mo(self):
        customer = self.env["res.partner"].search([], limit=1)
        so_line_vals = [
            {
                "product_id": self.product_service.id,
                "name": "Service",
                "product_uom_qty": 1.0,
                "price_unit": 100.0,
            },
            {
                "product_id": self.product_stock.id,
                "name": "Stockable",
                "product_uom_qty": 1.0,
                "price_unit": 100.0,
            },
        ]
        so = self.env["sale.order"].create(
            {
                "partner_id": customer.id,
                "order_line": [(0, 0, vals) for vals in so_line_vals],
                "analytic_account_id": self.analytic_account.id,
            }
        )
        so.action_confirm()
        so_analytic = so.analytic_account_id
        mo = self.env["mrp.production"].search(
            [("analytic_account_id", "=", so_analytic.id)]
        )
        self.assertEqual(len(mo), 1, "Expected one MO with the SO's Analytic Account")
