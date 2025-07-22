from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged("post_install", "-at_install")
class TestSaleOrderLineAnalyticDistribution(TransactionCase):
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
                "No income analytic account field found on product.template. "
                "Check the product_analytic module."
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
                "name": "Line with AA",
                "product_uom_qty": 1.0,
                "product_uom": cls.uom_unit.id,
                "price_unit": 100.0,
            }
        )

        cls.line_without = env["sale.order.line"].create(
            {
                "order_id": cls.so.id,
                "product_id": cls.product_without.id,
                "name": "Line without AA",
                "product_uom_qty": 1.0,
                "product_uom": cls.uom_unit.id,
                "price_unit": 50.0,
            }
        )

        # Line without product → make it "non accountable" to avoid SQL constraint
        cls.line_noproduct = env["sale.order.line"].create(
            {
                "order_id": cls.so.id,
                "name": "Line without product",
                "display_type": "line_note",
                "sequence": 99,
            }
        )

    # -------------------------
    # Utils
    # -------------------------
    def _recompute_distribution(self, lines):
        """Force the recompute of the analytic field in the past records."""
        lines.invalidate_cache(fnames=["analytic_distribution"])
        lines._compute_analytic_distribution()

    # -------------------------
    # Tests
    # -------------------------
    def test_distribution_is_set_from_product_income_account(self):
        """The line with analytic account should have 100% assigned to this account."""
        self._recompute_distribution(self.line_with)
        dist_raw = self.line_with.analytic_distribution or {}
        dist = {int(k): v for k, v in dist_raw.items()}
        self.assertEqual(dist, {self.aa_income.id: 100})

    def test_lines_without_account_are_left_to_super(self):
        """Lines without account should not receive forced distribution here."""
        lines = self.line_without | self.line_noproduct
        self._recompute_distribution(lines)
        self.assertFalse(bool(self.line_without.analytic_distribution))
        self.assertFalse(bool(self.line_noproduct.analytic_distribution))

    def test_mixed_recordset_branch_coverage(self):
        """Call compute with a mixed recordset to cover the
        OR (|=) and the `return super(...)`."""
        lines = self.line_with | self.line_without | self.line_noproduct
        self._recompute_distribution(lines)
        self.assertEqual(len(lines), 3)
