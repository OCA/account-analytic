# -*- coding: utf-8 -*-
# Copyright 2016 Carlos Dauden <carlos.dauden@tecnativa.com>
# Copyright 2017 Vicent Cubells <vicent.cubells@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import common


class TestSaleProcurementAnalytic(common.SavepointCase):
    """ Use case : Prepare some data for current test case """

    @classmethod
    def setUpClass(cls):
        super(TestSaleProcurementAnalytic, cls).setUpClass()
        cls.product = cls.env['product.product'].create({
            'name': 'Product Test',
        })
        cls.partner = cls.env['res.partner'].create({
            'name': 'Partner #1',
        })
        cls.analytic_account = cls.env['account.analytic.account'].create({
            'name': 'Test Analytic Account',
        })
        cls.sale_order = cls.env['sale.order'].create({
            'partner_id': cls.partner.id,
            'project_id': cls.analytic_account.id,
            'order_line': [(0, 0, {
                'product_id': cls.product.id,
                'product_uom_qty': 1,
                'price_unit': cls.product.list_price,
                'name': cls.product.name,
            })],
        })

    def test_sale_to_procurement(self):
        # Confirm the sale order
        self.sale_order.with_context(test_enabled=True).action_confirm()
        # Search procurement generate by sale order
        procurement = self.env['procurement.order'].search(
            [('account_analytic_id', '=', self.analytic_account.id)])
        self.assertTrue(procurement)
