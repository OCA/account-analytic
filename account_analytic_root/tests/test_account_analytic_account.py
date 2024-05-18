# Copyright 2015 Antiun Ingenieria - Javier Iniesta
# Copyright 2017 Tecnativa - Luis Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase


class TestAccountInvoiceLine(TransactionCase):

    def setUp(self):
        super().setUp()
        self.analytic_account_A = self.env['account.analytic.account'].create(
            {'name': 'test analytic_account_A'}
        )
        self.analytic_account_AB = self.env['account.analytic.account'].create(
            {
                'name': 'test analytic_account_AB',
                'parent_id': self.analytic_account_A.id,
            }
        )
        self.analytic_account_ABC = self.env['account.analytic.account'].create(
            {
                'name': 'test analytic_account_AB',
                'parent_id': self.analytic_account_AB.id,
            }
        )

    def test_root_if_no_parent_returns_itself(self):
        self.assertEqual(
            self.analytic_account_A, self.analytic_account_A.root_analytic_account_id
        )

    def test_root_if_parent(self):
        self.assertEqual(
            self.analytic_account_AB.root_analytic_account_id, self.analytic_account_A
        )

    def test_root_if_grand_parent(self):
        self.assertEqual(
            self.analytic_account_ABC.root_analytic_account_id, self.analytic_account_A
        )
