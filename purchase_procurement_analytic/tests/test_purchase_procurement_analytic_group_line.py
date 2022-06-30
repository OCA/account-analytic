# Copyright 2016 Carlos Dauden <carlos.dauden@tecnativa.com>
# Copyright 2017 Vicent Cubells <vicent.cubells@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import common

from .common import PurchaseAnalyticCommon


class TestPurchaseProcurementAnalytic(PurchaseAnalyticCommon, common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env.company.purchase_analytic_grouping = "line"

    def test_procurement_to_purchase(self):
        # Run procurements
        purchases_before = self.env["purchase.order"].search([])
        self.procurement_group_obj.run(self.procur_vals)
        purchases_after = self.env["purchase.order"].search([]) - purchases_before
        self.procurement_group_obj.run(self.procur_vals_2)
        purchases_after_2 = self.env["purchase.order"].search([]) - (
            purchases_after | purchases_before
        )

        self.assertFalse(
            purchases_after_2, "There should be just one purchase order generated"
        )
        self.assertEqual(2, len(purchases_after.order_line))
        # Make sure that PO line have analytic account
        self.assertEqual(
            len(
                purchases_after.order_line.filtered(
                    lambda line: line.account_analytic_id == self.analytic_account
                )
            ),
            1,
        )
