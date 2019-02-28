# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import common


class TestPurchaseProcurementAnalytic(common.SavepointCase):
    """ Use case : Prepare some data for current test case """

    @classmethod
    def setUpClass(cls):
        super(TestPurchaseProcurementAnalytic, cls).setUpClass()
        cls.AnalyticAccount = cls.env['account.analytic.account']
        cls.SaleOrderLine = cls.env['sale.order.line']
        cls.vendor = cls.env['res.partner'].create({
            'name': 'Partner #2',
        })
        cls.supplierinfo = cls.env['product.supplierinfo'].create({
            'name': cls.vendor.id,
        })
        cls.mto = cls.env.ref('stock.route_warehouse0_mto')
        cls.buy = cls.env.ref('purchase.route_warehouse0_buy')
        cls.product = cls.env['product.product'].create({
            'name': 'Product Test',
            'seller_ids': [(6, 0, [cls.supplierinfo.id])],
            'route_ids': [(6, 0, [cls.buy.id,
                                  cls.mto.id])],
        })
        cls.partner = cls.env['res.partner'].create({
            'name': 'Partner #1',
        })
        cls.analytic_account = cls.AnalyticAccount.create({
            'name': 'Test Analytic Account',
        })
        cls.analytic_account_2 = cls.AnalyticAccount.create({
            'name': 'Test Analytic Account2',
        })
        cls.analytic_account_3 = cls.AnalyticAccount.create({
            'name': 'Test Analytic Account2',
        })
        cls.sale_order = cls.env['sale.order'].create({
            'partner_id': cls.partner.id,
            'analytic_account_id': cls.analytic_account.id,
            'order_line': [(0, 0, {
                'product_id': cls.product.id,
                'product_uom_qty': 1,
                'price_unit': cls.product.list_price,
                'name': cls.product.name,
            })],
            'picking_policy': 'direct',
        })
        cls.sale_order2 = cls.env['sale.order'].create({
            'partner_id': cls.partner.id,
            'analytic_account_id': cls.analytic_account_3.id,
            'order_line': [(0, 0, {
                'product_id': cls.product.id,
                'product_uom_qty': 1,
                'price_unit': cls.product.list_price,
                'name': cls.product.name,
            })],
            'picking_policy': 'direct',
        })

    def test_sale_to_procurement(self):
        # No purchase order lines should initially be found with newly
        # created analytic account.
        purcahse_order = self.env['purchase.order.line'].search(
            [('account_analytic_id', '=', self.analytic_account.id)])
        self.assertFalse(purcahse_order)
        # One purchase order line should be found with newly created
        # analytic account after confirming sale order.
        self.sale_order.with_context(test_enabled=True).action_confirm()
        purcahse_order = self.env['purchase.order.line'].search(
            [('account_analytic_id', '=', self.analytic_account.id)])
        self.assertEquals(len(purcahse_order.order_id.order_line), 1)
        # Adding a new sale order line should merge a new purchase order line
        # into the existing purchase order line, as the analytic accounts
        # match. As a result, just one purchase order line should still be
        # found.
        self.SaleOrderLine.create({
            'product_id': self.product.id,
            'product_uom_qty': 1,
            'price_unit': self.product.list_price,
            'name': self.product.name,
            'order_id': self.sale_order.id
        })
        self.assertEquals(len(purcahse_order.order_id.order_line), 1)
        # Changing the analytic account on the purchase order line and then
        # adding a new line to the sale order should create a new purchase
        # order line, as the analytic accounts no longer match.
        purcahse_order.order_id.order_line[0].account_analytic_id =\
            self.analytic_account_2.id
        self.SaleOrderLine.create({
            'product_id': self.product.id,
            'product_uom_qty': 1,
            'price_unit': self.product.list_price,
            'name': self.product.name,
            'order_id': self.sale_order.id
        })
        self.assertEquals(len(purcahse_order.order_id.order_line), 2)
        # If no analytic accounts are set, purchase order lines should
        # get merged.
        po_linecount = len(self.env['purchase.order.line'].search([]))
        self.sale_order2.with_context(test_enabled=True).action_confirm()
        purcahse_order = self.env['purchase.order.line'].search(
            [('account_analytic_id', '=', self.analytic_account_3.id)])
        purcahse_order.order_id.order_line[0].account_analytic_id = []
        self.SaleOrderLine.create({
            'product_id': self.product.id,
            'product_uom_qty': 1,
            'price_unit': self.product.list_price,
            'name': self.product.name,
            'order_id': self.sale_order.id
        })
        self.assertEquals(
            len(self.env['purchase.order.line'].search([])), po_linecount + 1)
