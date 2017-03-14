# -*- coding: utf-8 -*-
# Copyright 2016 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import SavepointCase


class TestAccountAnalyticNoLines(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(TestAccountAnalyticNoLines, cls).setUpClass()

        # ENVIRONMENTS

        cls.account_account = cls.env['account.account']
        cls.account_analytic_line = cls.env['account.analytic.line']
        cls.account_journal = cls.env['account.journal']
        cls.account_move_line = cls.env['account.move.line']
        cls.account_invoice = cls.env['account.invoice']
        cls.account_invoice_line = cls.env['account.invoice.line']

        # INSTANCES

        # Instance: user
        cls.user = cls.env.ref('base.res_partner_2')

        # Instance: accounts
        cls.account_440000 = cls.account_account.create({
            'name': 'Entreprises liées',
            'code': '440000_demo',
            'user_type_id':
                cls.env.ref('account.data_account_type_payable').id,
            'reconcile': True})
        cls.account_550001 = cls.account_account.create({
            'name': 'Banque',
            'code': '550001_demo',
            'user_type_id':
                cls.env.ref('account.data_account_type_liquidity').id,
            'reconcile': False})
        cls.account_600000 = cls.account_account.create({
            'name': 'Achats de matières premières',
            'code': '600000_demo',
            'user_type_id':
                cls.env.ref('account.data_account_type_expenses').id,
            'reconcile': False})

        # Journal
        cls.journal = cls.account_journal.create({
            'name': 'Bank Journal Test',
            'type': 'bank',
            'code': 'BKTEST',
            'default_debit_account_id': cls.account_550001.id,
            'default_credit_account_id': cls.account_550001.id})

        # Invoice lines
        cls.invoice_line_1 = cls.account_invoice_line.create({
            'name': 'Test invoice line 1',
            'price_unit': 50,
            'quantity': 2,
            'account_id': cls.account_600000.id})
        cls.invoice_line_2 = cls.account_invoice_line.create({
            'name': 'Test invoice line 2',
            'price_unit': 25,
            'quantity': 2,
            'account_id': cls.account_600000.id})
        cls.invoice_line_3 = cls.account_invoice_line.create({
            'name': 'Test invoice line 3',
            'price_unit': 100,
            'quantity': 1,
            'account_id': cls.account_600000.id})
        cls.invoice_line_4 = cls.account_invoice_line.create({
            'name': 'Test invoice line 4',
            'price_unit': 1,
            'quantity': 0,
            'account_id': cls.account_600000.id})

        # Invoice
        cls.invoice = cls.account_invoice.create({
            'partner_id': cls.user.id,
            'account_id': cls.account_440000.id,
            'type': 'in_invoice',
            'invoice_line_ids': [(6, 0, [cls.invoice_line_1.id,
                                         cls.invoice_line_2.id,
                                         cls.invoice_line_3.id])]})
        cls.invoice_1 = cls.account_invoice.create({
            'partner_id': cls.user.id,
            'account_id': cls.account_440000.id,
            'type': 'in_invoice',
            'invoice_line_ids': [(6, 0, [cls.invoice_line_4.id])],
            'payment_term_id': cls.env.ref('account.account_payment_term').id,
        })

    def test_create_analytic_lines(self):
        """
        Test the expected result when the method ´create_analytic_lines` is
        called on an invoice.
        The expected result is that no analytic line has been created
        for this invoice.
        """
        move_lines = self.account_move_line.search([
            ('invoice_id', '=', self.invoice.id)])
        for line in move_lines:
            line.create_analytic_lines()

        analytic_lines =\
            self.account_analytic_line.search([
                ('move_id', 'in', move_lines.ids)]).ids
        self.assertFalse(analytic_lines)

    def test_finalize_invoice_move_lines_1(self):
        """
        Test the expected result when the method ´finalize_invoice_move_lines`
        is called on an invoice.
        The expected result is that no analytic line has been created
        for this invoice.
        """
        self.invoice.action_move_create()
        move_lines = self.account_move_line.search([
            ('invoice_id', '=', self.invoice.id)])
        analytic_lines = self.account_analytic_line.search(
            [('move_id', 'in', move_lines.ids)]).ids
        self.assertFalse(analytic_lines)

    def test_finalize_invoice_move_lines_2(self):
        """
        Test the expected result when the method ´finalize_invoice_move_lines`
        is called on an invoice with only one line with quantity == 0.
        The expected result is that no analytic line has been created
        for this invoice.
        """
        self.invoice_1.action_move_create()
        move_lines = self.account_move_line.search(
            [('invoice_id', '=', self.invoice.id)])
        analytic_lines = self.account_analytic_line.search(
            [('move_id', 'in', move_lines.ids)]).ids
        self.assertFalse(analytic_lines)
