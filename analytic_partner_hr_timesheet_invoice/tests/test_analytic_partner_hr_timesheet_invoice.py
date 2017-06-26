# -*- coding: utf-8 -*-
# Copyright 2017 Tecnativa - Luis M. Ontalba
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

import odoo.tests.common as common
from odoo import fields
from datetime import timedelta, datetime


class TestAnalyticPartnerHrTimesheetInvoice(common.SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(TestAnalyticPartnerHrTimesheetInvoice, cls).setUpClass()
        cls.order_partner = cls.env['res.partner'].create({
            'name': 'Test Order Partner',
        })
        cls.category = cls.env['product.category'].create({
            'name': 'Test Product Category',
        })
        cls.product = cls.env['product.product'].create({
            'name': 'Test Product',
            'sale_ok': True,
            'type': 'service',
            'categ_id': cls.category.id,
            'invoice_policy': 'order',
            'track_service': 'task',
        })
        cls.sale_order_vals = [
            (0, 0, {
                'product_id': cls.product.id,
                'name': 'Test Sale order Line',
                'product_uom_qty': 100.0,
                'price_unit': 50.00,
            })
        ]
        cls.sale_order = cls.env['sale.order'].create({
            'name': 'Test Sale Order',
            'partner_id': cls.order_partner.id,
            'order_line': cls.sale_order_vals,
        })
        cls.sale_order.action_confirm()
        cls.task = cls.env['project.task'].search(
            [('sale_line_id.id', '=', cls.sale_order.order_line[0].id)])
        cls.date_time = fields.Datetime.to_string(
            datetime.now() - timedelta(hours=1))
        cls.user = cls.env.user
        cls.analytic_account = cls.env['account.analytic.account'].create({
            'name': 'Test Analytic Account',
        })
        cls.analytic_line_1 = cls.env['account.analytic.line'].create({
            'date': cls.date_time,
            'user_id': cls.env.user.id,
            'name': 'Test Analytic line 1',
            'account_id': cls.analytic_account.id,
            'task_id': cls.task.id,
            'unit_amount': 10.0,
        })
        cls.analytic_line_2 = cls.env['account.analytic.line'].create({
            'date': cls.date_time,
            'user_id': cls.env.user.id,
            'name': 'Test Analytic line 2',
            'account_id': cls.analytic_account.id,
            'task_id': cls.task.id,
            'unit_amount': 10.0,
        })

    def test_global(self):
        self.analytic_line_1.other_partner_id = self.order_partner.id
        self.analytic_line_1.partner_id = False
        self.analytic_line_2.other_partner_id = False
        self.analytic_line_1.partner_id = self.order_partner.id
        invoice_id = self.sale_order.action_invoice_create()
        invoice = self.env['account.invoice'].browse(invoice_id)
        self.assertEqual(invoice.partner_id, self.order_partner)
        self.assertEqual(invoice.amount_untaxed, 5000)
