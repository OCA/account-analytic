# Copyright 2017 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.tests.common import TransactionCase


class TestAccountAnalyticSequence(TransactionCase):
    def setUp(self):
        super(TestAccountAnalyticSequence, self).setUp()

        self.analytic_account_obj = self.env['account.analytic.account']
        self.partner1 = self.env.ref('base.res_partner_1')
        self.analytic = self.analytic_account_obj.create(
            {'name': 'aa',
             'partner_id': self.partner1.id})

    def test_onchange(self):
        self.assertTrue(self.analytic.code, "Sequence not added")
