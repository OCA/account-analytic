# Copyright 2020 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase


class TestAccountAnalyticTagDefault(TransactionCase):
    def setUp(self):
        super().setUp()
        self.analytic_account_obj = self.env["account.analytic.account"]
        self.tag_obj = self.env["account.analytic.tag"]
        self.move_obj = self.env["account.move"]
        self.account_obj = self.env["account.account"]

        self.company = self.env.ref("base.main_company")
        self.partner1 = self.env.ref("base.res_partner_1")

        self.journal = self.journal_sale = self.env["account.journal"].create(
            {"name": "Test journal sale", "code": "SALE0", "type": "sale"}
        )
        self.account_sales = self.account_obj.create(
            {
                "code": "X1020",
                "name": "Product Sales - (test)",
                "user_type_id": self.env.ref("account.data_account_type_revenue").id,
            }
        )
        self.tag_01 = self.tag_obj.create({"name": "Tag 1"})
        self.tag_02 = self.tag_obj.create({"name": "Tag 2"})
        self.tag_03 = self.tag_obj.create({"name": "Tag 3"})

        self.test_analytic_account = self.analytic_account_obj.create(
            {"name": "Finance", "default_analytic_tag_ids": [(6, 0, [self.tag_01.id])]}
        )
        self.another_analytic_account = self.analytic_account_obj.create(
            {"name": "Finance", "default_analytic_tag_ids": [(6, 0, [self.tag_03.id])]}
        )

    def test_01_create_entry_no_tags(self):
        invoice = self.move_obj.with_context(default_move_type="out_invoice").create(
            {
                "move_type": "out_invoice",
                "company_id": self.company.id,
                "journal_id": self.journal.id,
                "partner_id": self.partner1.id,
                "invoice_line_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "[FURN_7800] Desk Combination",
                            "account_id": self.account_sales.id,
                            "price_unit": 1000.0,
                            "quantity": 1.0,
                            "product_id": self.ref("product.product_product_3"),
                            "analytic_account_id": self.test_analytic_account.id,
                        },
                    )
                ],
            }
        )
        self.assertEqual(invoice.invoice_line_ids.analytic_tag_ids, self.tag_01)
        # Change account, tags should change:
        invoice.invoice_line_ids.analytic_account_id = self.another_analytic_account
        self.assertEqual(invoice.invoice_line_ids.analytic_tag_ids, self.tag_03)

    def test_02_create_entry_with_different_tags(self):
        invoice = self.move_obj.with_context(default_move_type="out_invoice").create(
            {
                "move_type": "out_invoice",
                "company_id": self.company.id,
                "journal_id": self.journal.id,
                "partner_id": self.partner1.id,
                "invoice_line_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "[FURN_7800] Desk Combination",
                            "account_id": self.account_sales.id,
                            "price_unit": 1000.0,
                            "quantity": 1.0,
                            "product_id": self.ref("product.product_product_3"),
                            "analytic_account_id": self.test_analytic_account.id,
                            "analytic_tag_ids": [(6, 0, self.tag_02.ids)],
                        },
                    )
                ],
            }
        )
        self.assertEqual(invoice.invoice_line_ids.analytic_tag_ids, self.tag_02)
