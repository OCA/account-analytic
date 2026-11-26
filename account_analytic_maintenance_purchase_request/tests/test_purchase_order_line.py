from odoo.addons.base.tests.common import BaseCommon


class TestMaintenancePurchaseRequest(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.partner = cls.env["res.partner"].create({"name": "Test Partner"})
        cls.product = cls.env["product.product"].create(
            {
                "name": "Test Product",
                "is_storable": True,
            }
        )
        cls.analytic_account = cls.env["account.analytic.account"].create(
            {
                "name": "Maintenance Analytic Account",
                "plan_id": cls.env["account.analytic.plan"]
                .create({"name": "Maintenance Plan"})
                .id,
            }
        )
        cls.equipment = cls.env["maintenance.equipment"].create(
            {"name": "Test Equipment"}
        )
        cls.request = cls.env["maintenance.request"].create(
            {
                "name": "Test Request",
                "equipment_id": cls.equipment.id,
            }
        )

    def _create_purchase_order(self, **values):
        values.setdefault("partner_id", self.partner.id)
        return (
            self.env["purchase.order"]
            .with_context(maintenance_request_id=self.request.id)
            .create(values)
        )

    def _create_purchase_line(self, purchase, **values):
        values.update(
            {
                "order_id": purchase.id,
                "product_id": self.product.id,
                "name": self.product.name,
                "product_qty": 1,
                "price_unit": 100,
            }
        )
        return purchase.env["purchase.order.line"].create(values)

    def test_purchase_line_propagates_maintenance_distribution(self):
        distribution = {str(self.analytic_account.id): 100}
        self.equipment.analytic_distribution = distribution
        purchase = self._create_purchase_order()
        line = self._create_purchase_line(purchase)
        self.assertEqual(line.analytic_distribution, distribution)

    def test_purchase_line_without_maintenance_distribution(self):
        purchase = self._create_purchase_order()
        line = self._create_purchase_line(purchase)
        self.assertFalse(line.analytic_distribution)

    def test_purchase_line_without_maintenance_request(self):
        distribution = {str(self.analytic_account.id): 100}
        self.equipment.analytic_distribution = distribution
        purchase = self.env["purchase.order"].create({"partner_id": self.partner.id})
        line = self._create_purchase_line(purchase)
        self.assertFalse(line.analytic_distribution)
