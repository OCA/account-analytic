# Copyright 2023 Tecnativa - Víctor Martínez
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
            groups="{},{},{}".format(
                "account.group_account_invoice",
                "analytic.group_analytic_accounting",
                "account_analytic_tag.group_analytic_tags",
            ),
        )
        # ==== For Accounting ====
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
        # ==== Tags ====
        cls.account_analytic_tag_a = cls.env["account.analytic.tag"].create(
            {
                "name": "Tag Info A",
                "account_analytic_id": cls.analytic_account_a.id,
            }
        )
        cls.account_analytic_tag_b = cls.env["account.analytic.tag"].create(
            {
                "name": "Tag Info B",
                "account_analytic_id": cls.analytic_account_a.id,
            }
        )
        # ==== For Invoices ====
        cls.product_a = cls.env["product.product"].create(
            {
                "name": "product_a",
                "uom_id": cls.env.ref("uom.product_uom_unit").id,
                "lst_price": 100.0,
                "standard_price": 80.0,
                "taxes_id": False,
            }
        )
        cls.product_b = cls.env["product.product"].create(
            {
                "name": "product_b",
                "uom_id": cls.env.ref("uom.product_uom_unit").id,
                "lst_price": 200.0,
                "standard_price": 100.0,
                "taxes_id": False,
            }
        )
        cls.partner_a = cls.env["res.partner"].create({"name": "partner_a"})
