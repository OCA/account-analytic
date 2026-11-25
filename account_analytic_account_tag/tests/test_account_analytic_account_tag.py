# Copyright 2026 ForgeFlow S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import Command
from odoo.tests import Form

from odoo.addons.base.tests.common import BaseCommon


class TestAccountAnalyticAccountTag(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.tag = cls.env["account.analytic.tag"].create({"name": "Test Tag"})
        plan = cls.env["account.analytic.plan"].create({"name": "Test Plan"})
        cls.account = cls.env["account.analytic.account"].create(
            {
                "name": "Test Account",
                "plan_id": plan.id,
                "tag_ids": [Command.set(cls.tag.ids)],
            }
        )

    def test_copy_keeps_tags(self):
        self.assertEqual(self.account.copy().tag_ids, self.tag)

    def test_form_tags(self):
        other_tag = self.env["account.analytic.tag"].create({"name": "Other Tag"})
        with Form(self.account) as form:
            form.tag_ids.add(other_tag)
        self.assertEqual(self.account.tag_ids, self.tag | other_tag)

    def test_search_by_tag(self):
        accounts = self.env["account.analytic.account"].search(
            [("tag_ids", "in", self.tag.ids)]
        )
        self.assertEqual(accounts, self.account)
