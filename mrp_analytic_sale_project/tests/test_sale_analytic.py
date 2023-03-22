from odoo.tests import common


class TestSaleAnalytic(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        mfg_route = cls.env.ref("mrp.route_warehouse0_manufacture")
        mto_route = cls.env.ref("stock.route_warehouse0_mto")
        mto_route.active = True

        cls.product_service = cls.env["product.product"].create(
            {
                "name": "Service",
                "type": "service",
                "service_tracking": "task_in_project",
            }
        )
        cls.product_stock = cls.env["product.product"].create(
            {
                "name": "Storable",
                "type": "product",
                "route_ids": [(6, 0, [mfg_route.id, mto_route.id])],
            }
        )
        cls.bom_product_stock = cls.env["mrp.bom"].create(
            {"product_tmpl_id": cls.product_stock.product_tmpl_id.id}
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
            }
        )
        so.action_confirm()
        so_analytic = so.analytic_account_id
        mo = self.env["mrp.production"].search(
            [("analytic_account_id", "=", so_analytic.id)]
        )
        self.assertEqual(len(mo), 1, "Expected one MO with the SO's Analytic Account")
