# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import datetime

from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.addons.analytic_tag_default.tests.test_default_tag \
    import TestAnalyticTagDefault


class TestPurchaseAnalyticTagDefault(TestAnalyticTagDefault):

    def test_purchase_order_default(self):

        purchase_object = self.env['purchase.order']

        partner_demo = self.env.ref('base.partner_demo')

        self.product_uom_unit = self.env.ref('product.product_uom_unit')

        purchase_account = purchase_object.create({
            'partner_id': partner_demo.id,
            'order_line': [(0, 0, {
                'name': self.service_delivery.name,
                'product_id': self.service_delivery.id,
                'price_unit': self.service_delivery.list_price,
                'product_qty': 1,
                'product_uom': self.product_uom_unit.id,
                'date_planned': datetime.today().strftime(
                    DEFAULT_SERVER_DATETIME_FORMAT)
            })]
        })
        purchase_account.order_line._onchange_product_id()
        self.assertEqual(purchase_account.order_line.account_analytic_id,
                         self.analytic_account_absences)

        purchase_order_one_tag = purchase_object.create({
            'partner_id': partner_demo.id,
            'order_line': [(0, 0, {
                'name': self.service_order.name,
                'product_id': self.service_order.id,
                'price_unit': self.service_order.list_price,
                'product_qty': 1,
                'product_uom': self.product_uom_unit.id,
                'date_planned': datetime.today().strftime(
                    DEFAULT_SERVER_DATETIME_FORMAT)
            })]
        })
        purchase_order_one_tag.order_line._onchange_product_id()
        self.assertEqual(purchase_order_one_tag.order_line.analytic_tag_ids,
                         self.tag_a)

        purchase_order_multiple = purchase_object.create({
            'partner_id': partner_demo.id,
            'order_line': [(0, 0, {
                'name': self.service_cost.name,
                'product_id': self.service_cost.id,
                'price_unit': self.service_cost.list_price,
                'product_qty': 1,
                'product_uom': self.product_uom_unit.id,
                'date_planned': datetime.today().strftime(
                    DEFAULT_SERVER_DATETIME_FORMAT)
            })]
        })
        purchase_order_multiple.order_line._onchange_product_id()
        self.assertEqual(
            purchase_order_multiple.order_line.account_analytic_id,
            self.analytic_account_internal)
        self.assertEqual(len(
            purchase_order_multiple.order_line.analytic_tag_ids), 2)
        self.assertEqual(purchase_order_multiple.order_line.analytic_tag_ids,
                         self.tag_1 + self.tag_2)
