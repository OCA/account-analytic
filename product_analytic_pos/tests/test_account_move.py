from odoo.tests.common import TransactionCase


class TestAccountMoveLineAnalytic(TransactionCase):
    def setUp(self):
        super().setUp()
        self.ProductCategory = self.env["product.category"]
        self.ProductTemplate = self.env["product.template"]
        self.Product = self.env["product.product"]
        self.AccountMove = self.env["account.move"]
        self.AccountMoveLine = self.env["account.move.line"]

        # Create analytic distributions
        self.income_distribution = {"1": 50.0, "2": 50.0}
        self.expense_distribution = {"3": 100.0}

        # Category with analytic setup
        self.category = self.ProductCategory.create(
            {
                "name": "Test Category",
                "income_analytic_distribution": self.income_distribution,
                "expense_analytic_distribution": self.expense_distribution,
            }
        )

        # Product template & product
        self.product_template = self.ProductTemplate.create(
            {
                "name": "Analytic Product",
                "categ_id": self.category.id,
                "income_analytic_distribution": self.income_distribution,
                "expense_analytic_distribution": False,  # Let it fallback to category
            }
        )
        self.product = self.Product.create(
            {
                "product_tmpl_id": self.product_template.id,
            }
        )

        # Account and partner
        self.account = self.env["account.account"].create(
            {
                "name": "Revenue",
                "code": "X101",
                "account_type": "income",
            }
        )
        self.purchase_journal = self.env["account.journal"].create(
            {
                "name": "Purchase Journal",
                "code": "PURJ",
                "type": "purchase",
                "default_account_id": self.account.id,
            }
        )
        self.sale_journal = self.env["account.journal"].create(
            {
                "name": "Sales Journal",
                "code": "SALJ",
                "type": "sale",
                "default_account_id": self.account.id,
            }
        )
        self.partner = self.env["res.partner"].create({"name": "Test Partner"})

    def _create_move_line(self, move_type, extra_values=None):
        values = extra_values or {}
        move = self.AccountMove.create(
            {
                "move_type": move_type,
                "partner_id": self.partner.id,
                **values,
            }
        )
        line = self.AccountMoveLine.new(
            {
                "move_id": move.id,
                "account_id": self.account.id,
                "partner_id": self.partner.id,
                "product_id": self.product.id,
            }
        )
        line._compute_analytic_distribution()
        return line

    def test_income_invoice_uses_product_distribution(self):
        line = self._create_move_line(
            "out_invoice", {"journal_id": self.sale_journal.id}
        )
        self.assertEqual(
            line.analytic_distribution,
            self.income_distribution,
            "Should use product income analytic distribution for out_invoice",
        )

    def test_expense_invoice_falls_back_to_category(self):
        line = self._create_move_line(
            "in_invoice", {"journal_id": self.purchase_journal.id}
        )
        self.assertEqual(
            line.analytic_distribution,
            self.expense_distribution,
            "Should fallback to category expense analytic distribution",
        )

    def test_existing_analytic_distribution_is_not_overwritten(self):
        line = self._create_move_line("out_invoice")
        # Manually assign analytic distribution before recomputation
        custom = {"999": 100.0}
        line.analytic_distribution = custom
        line._compute_analytic_distribution()
        self.assertNotEqual(
            line.analytic_distribution,
            custom,
            "Existing analytic distribution must not be overwritten",
        )

    def test_unsupported_move_type_does_nothing(self):
        line = self._create_move_line("entry")  # Not in INV_TYPE_MAP
        self.assertFalse(
            line.analytic_distribution,
            "Unsupported move types should not set analytic distribution",
        )

    def test_no_product_does_nothing(self):
        move = self.AccountMove.create(
            {
                "move_type": "out_invoice",
                "partner_id": self.partner.id,
                "journal_id": self.env["account.journal"].search([], limit=1).id,
            }
        )
        line = self.AccountMoveLine.new(
            {
                "move_id": move.id,
                "account_id": self.account.id,
                "partner_id": self.partner.id,
            }
        )
        line._compute_analytic_distribution()
        self.assertFalse(
            line.analytic_distribution,
            "Lines without product should remain without analytic distribution",
        )
