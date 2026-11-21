from odoo.addons.base.tests.common import BaseCommon


class TestPurchaseOrderLine(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create({"name": "Test Vendor"})
        cls.analytic_plan = cls.env["account.analytic.plan"].create(
            {"name": "Maintenance Plan"}
        )
        cls.analytic_account = cls.env["account.analytic.account"].create(
            {
                "name": "Maintenance Analytic Account",
                "plan_id": cls.analytic_plan.id,
            }
        )
        cls.equipment_category = cls.env["maintenance.equipment.category"].create(
            {"name": "Test Equipment Category"}
        )
        cls.product = cls.env["product.product"].create(
            {
                "name": "Test Product",
                "purchase_equipment_category_id": cls.equipment_category.id,
                "type": "service",
            }
        )
        cls.purchase = cls.env["purchase.order"].create({"partner_id": cls.partner.id})
        cls.purchase_line = cls.env["purchase.order.line"].create(
            {
                "order_id": cls.purchase.id,
                "product_id": cls.product.id,
                "product_qty": 1,
                "price_unit": 100,
                "equipment_category_id": cls.equipment_category.id,
            }
        )

    def test_prepare_equipment_vals_propagates_analytic_distribution(self):
        distribution = {
            str(self.analytic_account.id): 100,
        }
        self.purchase_line.analytic_distribution = distribution
        self.purchase.button_confirm()
        self.assertTrue(self.purchase_line.equipment_ids)
        self.assertEqual(
            self.purchase_line.equipment_ids.analytic_distribution, distribution
        )

    def test_prepare_equipment_vals_without_analytic_distribution(self):
        self.purchase.button_confirm()
        self.assertTrue(self.purchase_line.equipment_ids)
        self.assertFalse(self.purchase_line.equipment_ids.analytic_distribution)
