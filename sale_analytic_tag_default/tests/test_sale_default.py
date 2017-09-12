# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.analytic_tag_default.tests.test_default_tag \
    import TestAnalyticTagDefault


class TestSaleAnalyticTagDefault(TestAnalyticTagDefault):

    def test_sale_order_default(self):

        partner_demo = self.env.ref('base.partner_demo')

        self.product_uom_unit = self.env.ref('product.product_uom_unit')

        sale_order_one_tag = self.env['sale.order'].create({
            'partner_id': partner_demo.id,
            'order_line': [(0, 0, {
                'name': self.service_order.name,
                'product_id': self.service_order.id,
                'price_unit': self.service_order.list_price,
                'product_uom_qty': 1,
                'product_uom': self.product_uom_unit.id,
            })]
        })
        sale_order_one_tag.order_line._onchange_product_id()
        self.assertEqual(sale_order_one_tag.order_line.analytic_tag_ids,
                         self.tag_a)

        sale_order_multiple = self.env['sale.order'].create({
            'partner_id': partner_demo.id,
            'order_line': [(0, 0, {
                'name': self.service_cost.name,
                'product_id': self.service_cost.id,
                'price_unit': self.service_cost.list_price,
                'product_uom_qty': 1,
                'product_uom': self.product_uom_unit.id,
            })]
        })
        sale_order_multiple.order_line._onchange_product_id()
        self.assertEqual(len(
            sale_order_multiple.order_line.analytic_tag_ids), 2)
        self.assertEqual(sale_order_multiple.order_line.analytic_tag_ids,
                         self.tag_1 + self.tag_2)
