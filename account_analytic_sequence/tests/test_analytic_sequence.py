# Copyright 2017 ACSONE SA/NV
# Copyright 2020 Brainbean Apps (https://brainbeanapps.com)
# Copyright 2024 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.base.tests.common import BaseCommon


class TestAccountAnalyticSequence(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.analytic_account_obj = cls.env["account.analytic.account"]
        cls.plan = cls.env["account.analytic.plan"].create({"name": "Test plan"})
        cls.analytic = cls.analytic_account_obj.create(
            {"name": "aa", "partner_id": cls.partner.id, "plan_id": cls.plan.id}
        )

    def test_account_analytic_account_code(self):
        self.assertTrue(self.analytic.code, "Sequence not added")
        analytic2 = self.analytic_account_obj.create(
            {"name": "Test 2", "plan_id": self.plan.id, "code": "TEST"}
        )
        self.assertEqual(analytic2.code, "TEST")
