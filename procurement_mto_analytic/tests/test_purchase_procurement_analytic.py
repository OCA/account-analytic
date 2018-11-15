# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import common


class TestPurchaseProcurementAnalytic(common.SavepointCase):
    """ Use case : Prepare some data for current test case """

    @classmethod
    def setUpClass(cls):
        super(TestPurchaseProcurementAnalytic, cls).setUpClass()
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
        cls.analytic_account = cls.env['account.analytic.account'].create({
            'name': 'Test Analytic Account',
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

    def test_sale_to_procurement(self):
        self.sale_order.with_context(test_enabled=True).action_confirm()

        purcahse_order = self.env['purchase.order.line'].search(
            [('account_analytic_id', '=', self.analytic_account.id)])
        self.assertTrue(purcahse_order)
