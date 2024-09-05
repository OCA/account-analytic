# Copyright 2023 Tecnativa - Víctor Martínez
# Copyright 2024 APSL-Nagarro - Miquel Alzanillas
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from odoo.tests import common, new_test_user, tagged


@tagged("post_install", "-at_install")
class TestAccountAnalyticTagBase(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(
            context=dict(
                cls.env.context,
                mail_create_nolog=True,
                mail_create_nosubscribe=True,
                mail_notrack=True,
                no_reset_password=True,
                tracking_disable=True,
            )
        )
        cls.user = new_test_user(
            cls.env,
            login="test-analytic-tag-user",
            groups="account.group_account_invoice, analytic.group_analytic_accounting, \
                    account_analytic_tag.group_analytic_tags",
        )
        # ==== For Accounting ====
        cls.default_company_id = cls.env["res.company"].browse(1)
        # Set chart template
        cls.default_company_id._chart_template_selection()
        cls.default_journal_id = cls.env["account.journal"].create(
            {"name": "Test Journal", "type": "sale", "code": "TST"}
        )
        cls.default_plan = cls.env["account.analytic.plan"].create({"name": "Default"})

        cls.analytic_account_a = cls.env["account.analytic.account"].create(
            {
                "name": "analytic_account_a",
                "plan_id": cls.default_plan.id,
            }
        )
        cls.analytic_account_b = cls.env["account.analytic.account"].create(
            {
                "name": "analytic_account_b",
                "plan_id": cls.default_plan.id,
            }
        )
        cls.analytic_account_c = cls.env["account.analytic.account"].create(
            {
                "name": "analytic_account_c",
                "plan_id": cls.default_plan.id,
            }
        )
        # ==== Tags ====
        cls.account_analytic_tag_spread_default = cls.env[
            "account.analytic.tag"
        ].create(
            {
                "name": "Tag Spread No Filter",
                "to_spread": 1,
            }
        )

        cls.account_analytic_tag_spread_with_exclusion = cls.env[
            "account.analytic.tag"
        ].create(
            {
                "name": "Tag Spread Exclude",
                "to_spread": 1,
                "spread_filter_operation": "exclude",
                "spread_filter_analytic_account_ids": [
                    (6, 0, [cls.analytic_account_a.id])
                ],
            }
        )
        cls.account_analytic_tag_spread_with_inclusion = cls.env[
            "account.analytic.tag"
        ].create(
            {
                "name": "Tag Spread Include",
                "to_spread": 1,
                "spread_filter_operation": "include",
                "spread_filter_analytic_account_ids": [
                    (6, 0, [cls.analytic_account_a.id])
                ],
            }
        )
        # Set tags for analytic accounts
        cls.analytic_account_a.write(
            {
                "mapped_analytic_tag_ids": [
                    (
                        6,
                        0,
                        [
                            cls.account_analytic_tag_spread_default.id,
                            cls.account_analytic_tag_spread_with_exclusion.id,
                            cls.account_analytic_tag_spread_with_inclusion.id,
                        ],
                    )
                ]
            }
        )
        cls.analytic_account_b.write(
            {
                "mapped_analytic_tag_ids": [
                    (
                        6,
                        0,
                        [
                            cls.account_analytic_tag_spread_default.id,
                            cls.account_analytic_tag_spread_with_exclusion.id,
                            cls.account_analytic_tag_spread_with_inclusion.id,
                        ],
                    )
                ]
            }
        )
        cls.analytic_account_c.write(
            {
                "mapped_analytic_tag_ids": [
                    (
                        6,
                        0,
                        [
                            cls.account_analytic_tag_spread_default.id,
                            cls.account_analytic_tag_spread_with_exclusion.id,
                            cls.account_analytic_tag_spread_with_inclusion.id,
                        ],
                    )
                ]
            }
        )

        # ==== For Invoices ====
        cls.product_a = cls.env["product.product"].create(
            {
                "name": "product_a",
                "uom_id": cls.env.ref("uom.product_uom_unit").id,
                "lst_price": 1000.0,
                "standard_price": 80.0,
                "taxes_id": False,
            }
        )
        cls.product_b = cls.env["product.product"].create(
            {
                "name": "product_b",
                "uom_id": cls.env.ref("uom.product_uom_unit").id,
                "lst_price": 1000.0,
                "standard_price": 80.0,
                "taxes_id": False,
            }
        )
        cls.product_c = cls.env["product.product"].create(
            {
                "name": "product_c",
                "uom_id": cls.env.ref("uom.product_uom_unit").id,
                "lst_price": 1000.0,
                "standard_price": 80.0,
                "taxes_id": False,
            }
        )
        cls.partner_a = cls.env["res.partner"].create({"name": "partner_a"})
