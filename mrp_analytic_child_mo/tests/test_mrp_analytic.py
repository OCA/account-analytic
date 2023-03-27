from odoo.tests import common


class TestMrpAnalytic(common.TransactionCase):
    def setUp(self):
        super().setUp()

        AnalyticAccount = self.env["account.analytic.account"]
        Product = self.env["product.product"]

        analytic_plan = self.env["account.analytic.plan"].create(
            {"name": "Plan Test", "company_id": False}
        )
        self.analytic_x = AnalyticAccount.create(
            {"name": "Analytic X", "plan_id": analytic_plan.id}
        )

        mfg_route = self.env.ref("mrp.route_warehouse0_manufacture")
        mto_route = self.env.ref("stock.route_warehouse0_mto")
        mto_route.active = True

        self.product_subassembly = Product.create(
            {
                "name": "Subassembly",
                "type": "product",
                "route_ids": [(6, 0, [mfg_route.id, mto_route.id])],
            }
        )
        self.product_final = Product.create(
            {
                "name": "Manufactured",
                "type": "product",
                "route_ids": [(6, 0, [mfg_route.id, mto_route.id])],
            }
        )
        self.bom_product_final = self.env["mrp.bom"].create(
            {
                "product_tmpl_id": self.product_final.product_tmpl_id.id,
                "bom_line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product_subassembly.id,
                            "product_uom_id": self.product_subassembly.uom_id.id,
                            "product_qty": 1.0,
                        },
                    )
                ],
            }
        )
        self.bom_product_subassembly = self.env["mrp.bom"].create(
            {"product_tmpl_id": self.product_subassembly.product_tmpl_id.id}
        )

    def test_101_create_analytic_to_child_mo(self):
        ManufacturingOrder = self.env["mrp.production"]
        mo = ManufacturingOrder.create(
            {
                "product_id": self.product_final.id,
                "product_uom_id": self.product_final.uom_id.id,
                "bom_id": self.bom_product_final.id,
                "analytic_account_id": self.analytic_x.id,
            }
        )
        mo.action_confirm()
        child_mo = self.env["mrp.production"].search(
            [("product_id", "=", self.product_subassembly.id)]
        )
        self.assertEqual(
            child_mo.analytic_account_id,
            self.analytic_x,
            "New Child MO expected to have the parent MO Analytic Account",
        )

    def test_102_update_analytic_to_child_mo(self):
        ManufacturingOrder = self.env["mrp.production"]
        mo = ManufacturingOrder.create(
            {
                "product_id": self.product_final.id,
                "product_uom_id": self.product_final.uom_id.id,
                "bom_id": self.bom_product_final.id,
            }
        )
        mo.action_confirm()
        mo.analytic_account_id = self.analytic_x
        child_mo = self.env["mrp.production"].search(
            [("product_id", "=", self.product_subassembly.id)]
        )
        self.assertEqual(
            child_mo.analytic_account_id,
            self.analytic_x,
            "Updated Child MO expected to have the parent MO Analytic Account",
        )
