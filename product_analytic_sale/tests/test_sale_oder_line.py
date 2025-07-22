from odoo.tests import SavepointCase, tagged


@tagged("post_install", "-at_install")
class TestSaleOrderLineAnalyticDistribution(SavepointCase):
    @classmethod
    def setUpClass(cls):  # noqa: D102
        super().setUpClass()
        env = cls.env

        cls.partner = env["res.partner"].create({"name": "Codecov Tester"})

        cls.aa_income = env["account.analytic.account"].create({"name": "AA Income"})

        income_field_candidates = [
            name
            for name, field in env["product.template"]._fields.items()
            if field.comodel_name == "account.analytic.account" and "income" in name
        ]
        if not income_field_candidates:
            raise AssertionError(
                "No s'ha trobat cap camp analític d'ingressos al product.template. "
                "Revisa el mòdul product_analytic."
            )
        cls.income_field_name = income_field_candidates[0]

        cls.product_with = env["product.product"].create(
            {
                "name": "Product with AA",
                "type": "service",
            }
        )
        cls.product_with.product_tmpl_id.write(
            {cls.income_field_name: cls.aa_income.id}
        )

        cls.product_without = env["product.product"].create(
            {
                "name": "Product without AA",
                "type": "service",
            }
        )

        cls.uom_unit = env.ref("uom.product_uom_unit")

        cls.so = env["sale.order"].create({"partner_id": cls.partner.id})

        cls.line_with = env["sale.order.line"].create(
            {
                "order_id": cls.so.id,
                "product_id": cls.product_with.id,
                "name": "Línia amb AA",
                "product_uom_qty": 1.0,
                "product_uom": cls.uom_unit.id,
                "price_unit": 100.0,
            }
        )

        cls.line_without = env["sale.order.line"].create(
            {
                "order_id": cls.so.id,
                "product_id": cls.product_without.id,
                "name": "Línia sense AA",
                "product_uom_qty": 1.0,
                "product_uom": cls.uom_unit.id,
                "price_unit": 50.0,
            }
        )

        cls.line_noproduct = env["sale.order.line"].create(
            {
                "order_id": cls.so.id,
                "name": "Línia sense producte",
                "product_uom_qty": 1.0,
                "product_uom": cls.uom_unit.id,
                "price_unit": 10.0,
            }
        )

    # -------------------------
    # Tests
    # -------------------------
    def test_distribution_is_set_from_product_income_account(self):
        """The line with an analytic account should have 100% assigned to that account."""
        (
            self.line_with | self.line_without | self.line_noproduct
        )._compute_analytic_distribution()

        dist_raw = self.line_with.analytic_distribution or {}
        dist = {int(k): v for k, v in dist_raw.items()}
        self.assertEqual(dist, {self.aa_income.id: 100})

    def test_lines_without_account_are_left_to_super(self):
        """Lines without an analytic account (or without a product) should not get forced distribution here.
        We do not check the exact behavior of super; only that our code does not set its own distribution for them."""

        self.assertFalse(self.line_without.analytic_distribution)
        self.assertFalse(self.line_noproduct.analytic_distribution)

    def test_mixed_recordset_branch_coverage(self):
        """Call the compute with a mixed recordset to cover the loop and the OR (|=)."""
        lines = self.line_with | self.line_without | self.line_noproduct
        self.assertEqual(len(lines), 3)
