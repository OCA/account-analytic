# Copyright 2023 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import Form, TransactionCase


class TestPartnerAnalytic(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))

        # Models
        cls.account_model = cls.env["account.account"]
        cls.account_move_model = cls.env["account.move"]
        cls.account_move_line_model = cls.env["account.move.line"]
        cls.analytic_account_model = cls.env["account.analytic.account"]
        cls.account_journal_model = cls.env["account.journal"]
        cls.account_type_model = cls.env["account.account.type"]
        cls.template_model = cls.env["product.template"]
        cls.partner_model = cls.env["res.partner"]
        cls.company_model = cls.env["res.company"]

        # Instances
        cls.company_1 = cls.company_model.create({"name": "Company 1"})
        cls.company_2 = cls.company_model.create({"name": "Company 2"})
        cls.journal_sale = cls.account_journal_model.create(
            {
                "name": "Test journal sale",
                "code": "Sale",
                "type": "sale",
                "company_id": cls.company_1.id,
            }
        )
        cls.journal_purchase_1 = cls.account_journal_model.create(
            {
                "name": "Test journal purchase 1",
                "code": "Purchase",
                "type": "purchase",
                "company_id": cls.company_1.id,
            }
        )
        cls.journal_purchase_2 = cls.account_journal_model.create(
            {
                "name": "Test journal purchase 2",
                "code": "Purchase",
                "type": "purchase",
                "company_id": cls.company_2.id,
            }
        )
        cls.analytic_account = cls.analytic_account_model.create(
            {"name": "Test Analytic Account 1", "company_id": cls.company_1.id}
        )
        cls.account_type = cls.account_type_model.create(
            {"name": "Test account type", "type": "other", "internal_group": "equity"}
        )
        cls.account_1 = cls.account_model.create(
            {
                "name": "Test Account 1",
                "code": "100",
                "user_type_id": cls.account_type.id,
                "company_id": cls.company_1.id,
            }
        )
        cls.account_2 = cls.account_model.create(
            {
                "name": "Test Account 2",
                "code": "101",
                "user_type_id": cls.account_type.id,
                "company_id": cls.company_2.id,
            }
        )
        cls.partner = cls.partner_model.create({"name": "Test Partner 1"})
        cls.partner.with_company(cls.company_1.id).write(
            {
                "property_account_receivable_id": cls.account_1.id,
                "property_account_payable_id": cls.account_1.id,
            }
        )
        cls.partner.with_company(cls.company_2.id).write(
            {
                "property_account_receivable_id": cls.account_2.id,
                "property_account_payable_id": cls.account_2.id,
            }
        )
        cls.template = cls.template_model.create(
            {"name": "Test Template", "list_price": 50, "standard_price": 50}
        )
        cls.product = cls.template.product_variant_ids

    @classmethod
    def _create_move(cls, partner, journal, company, account, product, bill=True):
        move = cls.account_move_model.create(
            {
                "partner_id": partner.id,
                "journal_id": journal.id,
                "move_type": "in_invoice" if bill else "out_invoice",
                "company_id": company.id,
            }
        )
        cls.account_move_line_model.create(
            {
                "move_id": move.id,
                "name": "Test Line",
                "quantity": 1,
                "price_unit": 0,
                "account_id": account.id,
                "product_id": product.id,
                "exclude_from_invoice_tab": False,
            }
        )
        return move

    def test_01_create_invoice_without_partner_analytic_account(self):
        """
        Do not assign a default Analytic Account on the partner and check that no
        Analytic Account has been set on the Invoice Line.
        """
        invoice = self._create_move(
            self.partner,
            self.journal_sale,
            self.company_1,
            self.account_1,
            self.product,
            bill=False,
        )
        invoice_line = invoice.invoice_line_ids[0]
        self.assertFalse(invoice_line.analytic_account_id)

    def test_02_create_invoice_with_partner_analytic_account(self):
        """
        Assign the Analytic Account to the partner and then when creating a new Invoice
        for the partner, the Analytic Account should be set as default.
        """
        company_id = self.company_1.id
        self.partner.with_company(company_id).write(
            {"property_analytic_account_id": self.analytic_account.id}
        )
        invoice = self._create_move(
            self.partner,
            self.journal_sale,
            self.company_1,
            self.account_1,
            self.product,
            bill=False,
        )
        invoice_line = invoice.invoice_line_ids[0]
        self.assertEqual(
            invoice_line.analytic_account_id,
            self.partner.with_company(company_id).property_analytic_account_id,
        )

    def test_03_create_bill_with_partner_analytic_account(self):
        """
        Assign the Analytic Account to the partner and then when creating a new Bill
        for the partner, the Analytic Account should be set as default.
        """
        company_id = self.company_1.id
        self.partner.with_company(company_id).write(
            {"property_supplier_analytic_account_id": self.analytic_account.id}
        )
        bill = self._create_move(
            self.partner,
            self.journal_purchase_1,
            self.company_1,
            self.account_1,
            self.product,
        )
        bill_line = bill.invoice_line_ids[0]
        self.assertEqual(
            bill_line.analytic_account_id,
            self.partner.with_company(company_id).property_supplier_analytic_account_id,
        )

    def test_04_create_bill_for_different_company(self):
        """
        Assign the Analytic Account to one company and create a Bill for a different
        company. The Analytic Account on the Bill Line should be empty as it is from a
        different company.
        """
        company_id = self.company_1.id
        self.partner.with_company(company_id).write(
            {"property_supplier_analytic_account_id": self.analytic_account.id}
        )
        bill = self._create_move(
            self.partner,
            self.journal_purchase_2,
            self.company_2,
            self.account_2,
            self.product,
        )
        bill_line = bill.invoice_line_ids[0]
        self.assertFalse(bill_line.analytic_account_id)

    def test_05_create_bill_from_interface(self):
        """
        Check that the Analytic Account is also set if the user creates the Bill via
        the user interface.
        """
        company_id = self.company_1.id
        self.partner.with_company(company_id).write(
            {"property_supplier_analytic_account_id": self.analytic_account.id}
        )
        form = Form(
            self.account_move_model.with_company(company_id).with_context(
                default_move_type="in_invoice",
                default_journal_id=self.journal_purchase_1.id,
            )
        )
        form.partner_id = self.partner
        with form.invoice_line_ids.new() as line:
            line.product_id = self.product
            line.account_id = self.account_1
        move = form.save()
        bill_line = move.invoice_line_ids.filtered(
            lambda line: line.product_id == self.product
        )
        self.assertEqual(len(bill_line), 1)
        self.assertEqual(
            bill_line.analytic_account_id,
            self.partner.with_company(company_id).property_supplier_analytic_account_id,
        )
