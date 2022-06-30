# Copyright 2016 Carlos Dauden <carlos.dauden@tecnativa.com>
# Copyright 2017 Vicent Cubells <vicent.cubells@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import common

from .common import PurchaseAnalyticCommon


class TestPurchaseProcurementAnalyticGroup(
    PurchaseAnalyticCommon, common.SavepointCase
):
    def test_purchase_grouping(self):
        purchases_before = self.env["purchase.order"].search([])
        self.procurement_group_obj.run(self.procur_vals)
        self.procurement_group_obj.run(self.procur_vals_2)
        purchases_after = self.env["purchase.order"].search([]) - purchases_before
        # Testing two purchase orders have been generated
        self.assertEqual(2, len(purchases_after))
