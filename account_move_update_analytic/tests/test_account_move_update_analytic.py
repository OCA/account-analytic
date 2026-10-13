# Copyright 2026 Factor3
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import Command, fields
from odoo.exceptions import ValidationError
from odoo.tests import tagged

from odoo.addons.account.tests.common import AccountTestInvoicingCommon


@tagged("post_install", "-at_install")
class TestAccountMoveUpdateAnalytic(AccountTestInvoicingCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env.user.group_ids = [
            Command.link(cls.env.ref("analytic.group_analytic_accounting").id)
        ]
        cls.plan = cls.env["account.analytic.plan"].create(
            {"name": "Test plan", "default_applicability": "optional"}
        )
        cls.analytic_account, cls.other_analytic_account = cls.env[
            "account.analytic.account"
        ].create(
            [
                {"name": name, "plan_id": cls.plan.id, "company_id": False}
                for name in ("Test account", "Other test account")
            ]
        )
        cls.distribution = {str(cls.analytic_account.id): 100.0}
        cls.other_distribution = {str(cls.other_analytic_account.id): 100.0}
        cls.incomplete_distribution = {str(cls.other_analytic_account.id): 50.0}

    def _create_bill(self, company_data=None, move_type="in_invoice", post=True):
        company_data = company_data or self.company_data
        is_sale = move_type == "out_invoice"
        journal = company_data[
            "default_journal_sale" if is_sale else "default_journal_purchase"
        ]
        account = company_data[
            "default_account_revenue" if is_sale else "default_account_expense"
        ]
        bill = (
            self.env["account.move"]
            .with_company(company_data["company"])
            .create(
                {
                    "move_type": move_type,
                    "partner_id": self.partner_a.id,
                    "journal_id": journal.id,
                    "invoice_date": fields.Date.today(),
                    "invoice_line_ids": [
                        Command.create(
                            {
                                "name": name,
                                "account_id": account.id,
                                "quantity": 1.0,
                                "price_unit": 100.0,
                                "tax_ids": [Command.clear()],
                                "analytic_distribution": self.distribution,
                            }
                        )
                        for name in ("First line", "Second line")
                    ],
                }
            )
        )
        if post:
            bill.action_post()
        return bill

    def _create_wizard(self, records, distribution):
        return (
            self.env["account.move.update.analytic.wizard"]
            .with_context(
                active_model=records._name,
                active_id=records[0].id,
                active_ids=records.ids,
            )
            .create({"analytic_distribution": distribution})
        )

    def _create_applicability_rule(self, **values):
        return self.env["account.analytic.applicability"].create(
            {
                "analytic_plan_id": self.plan.id,
                "business_domain": "bill",
                "applicability": "mandatory",
                **values,
            }
        )

    def _assert_rejected_update(self, records, distribution):
        lines = (
            records
            if records._name == "account.move.line"
            else records.invoice_line_ids
        )
        before = lines.read(["analytic_distribution", "analytic_line_ids"])
        wizard = self._create_wizard(records, distribution)

        # assertRaises rolls back a savepoint, which would conceal partial writes.
        try:
            wizard.update_analytic_lines()
        except ValidationError:
            self.assertEqual(
                lines.read(["analytic_distribution", "analytic_line_ids"]), before
            )
        else:
            self.fail("An incomplete mandatory distribution was accepted")

    def test_vendor_bill_rule_rejects_incomplete_distribution(self):
        self._create_applicability_rule()
        bill = self._create_bill()

        for distribution in (self.incomplete_distribution, False):
            with self.subTest(distribution=distribution):
                self._assert_rejected_update(bill.invoice_line_ids[0], distribution)

    def test_account_prefix_rule_rejects_incomplete_distribution(self):
        self._create_applicability_rule(
            account_prefix=self.company_data["default_account_expense"].code
        )
        bill = self._create_bill()

        self._assert_rejected_update(
            bill.invoice_line_ids[0], self.incomplete_distribution
        )

    def test_product_category_rule_applies_to_matching_line(self):
        self._create_applicability_rule(product_categ_id=self.product_a.categ_id.id)
        bill = self._create_bill(post=False)
        bill.invoice_line_ids[0].product_id = self.product_a
        bill.invoice_line_ids.analytic_distribution = self.distribution
        bill.action_post()

        self._assert_rejected_update(
            bill.invoice_line_ids[0], self.incomplete_distribution
        )
        line = bill.invoice_line_ids[1]
        self._create_wizard(line, self.incomplete_distribution).update_analytic_lines()
        self.assertEqual(line.analytic_distribution, self.incomplete_distribution)

    def test_optional_bill_rule_overrides_mandatory_default(self):
        self.plan.default_applicability = "mandatory"
        self._create_applicability_rule(applicability="optional")
        bill = self._create_bill()
        line = bill.invoice_line_ids[0]

        self._create_wizard(line, self.incomplete_distribution).update_analytic_lines()

        self.assertEqual(line.analytic_distribution, self.incomplete_distribution)

    def test_display_lines_do_not_block_optional_expense_allocations(self):
        self._create_applicability_rule()
        self._create_applicability_rule(
            applicability="optional",
            account_prefix=self.company_data["default_account_expense"].code,
        )

        for display_type in ("line_section", "line_note"):
            with self.subTest(display_type=display_type):
                bill = self._create_bill(post=False)
                bill.invoice_line_ids.analytic_distribution = False
                bill.invoice_line_ids = [
                    Command.create(
                        {
                            "name": "Services",
                            "display_type": display_type,
                            "sequence": 0,
                        }
                    ),
                ]
                bill.action_post()
                expense_lines = bill.invoice_line_ids.filtered(
                    lambda line: line.display_type == "product"
                )

                self._create_wizard(
                    bill, self.incomplete_distribution
                ).update_analytic_lines()

                self.assertEqual(
                    expense_lines.mapped("analytic_distribution"),
                    [self.incomplete_distribution] * 2,
                )

    def test_vendor_bill_rule_does_not_apply_to_customer_invoice(self):
        self._create_applicability_rule()
        invoice = self._create_bill(move_type="out_invoice")
        line = invoice.invoice_line_ids[0]

        self._create_wizard(line, self.incomplete_distribution).update_analytic_lines()

        self.assertEqual(line.analytic_distribution, self.incomplete_distribution)

    def test_whole_bill_validates_later_mandatory_line_before_writing(self):
        account = self.company_data["default_account_expense"].copy(
            {"name": "Rule-matched expense", "code": "987651"}
        )
        self._create_applicability_rule(account_prefix=account.code)
        bill = self._create_bill(post=False)
        bill.invoice_line_ids[1].account_id = account
        bill.action_post()

        self._assert_rejected_update(bill, self.incomplete_distribution)

    def test_display_lines_do_not_exempt_mandatory_expense_allocations(self):
        self._create_applicability_rule()
        bill = self._create_bill(post=False)
        bill.invoice_line_ids = [
            Command.create({"name": "Services", "display_type": display_type})
            for display_type in ("line_section", "line_note")
        ]
        bill.action_post()

        self._assert_rejected_update(bill, self.incomplete_distribution)

    def test_whole_bill_accepts_complete_distribution_under_rule(self):
        self._create_applicability_rule()
        bill = self._create_bill()

        self._create_wizard(bill, self.other_distribution).update_analytic_lines()

        for line in bill.invoice_line_ids:
            self.assertEqual(line.analytic_distribution, self.other_distribution)
            self.assertRecordValues(
                line.analytic_line_ids,
                [
                    {
                        self.plan._column_name(): self.other_analytic_account.id,
                        "amount": -line.balance,
                    }
                ],
            )

    def test_batch_validates_company_dependent_defaults_per_bill(self):
        other_data = self.setup_other_company()
        other_company = other_data["company"]
        self.env.user.company_ids = [Command.link(other_company.id)]
        self.env = self.env(
            context={
                **self.env.context,
                "allowed_company_ids": [self.env.company.id, other_company.id],
            }
        )
        self.plan.with_company(other_company).default_applicability = "mandatory"
        bill = self._create_bill()
        other_bill = self._create_bill(company_data=other_data)
        bills = bill + other_bill

        self._assert_rejected_update(bills, self.incomplete_distribution)
        self._create_wizard(bills, self.other_distribution).update_analytic_lines()
        for line in bills.invoice_line_ids:
            self.assertEqual(line.analytic_distribution, self.other_distribution)

    def test_rule_for_another_company_does_not_require_distribution(self):
        other_company = self.setup_other_company()["company"]
        self._create_applicability_rule(company_id=other_company.id)
        bill = self._create_bill()
        line = bill.invoice_line_ids[0]

        self._create_wizard(line, self.incomplete_distribution).update_analytic_lines()

        self.assertEqual(line.analytic_distribution, self.incomplete_distribution)

    def test_mandatory_default_rejects_incomplete_distribution(self):
        self.plan.default_applicability = "mandatory"
        bill = self._create_bill()

        self._assert_rejected_update(
            bill.invoice_line_ids[0], self.incomplete_distribution
        )
