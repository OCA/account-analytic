# Copyright 2020 Ecosoft Co., Ltd (http://ecosoft.co.th/).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.tests import common


class TestMrpAnalytic(common.TransactionCase):
    def setUp(self):
        super(TestMrpAnalytic, self).setUp()
        self.analytic_account = self.env["account.analytic.account"].create(
            {"name": "Analytic account test"}
        )
        self.product = self.env["product.product"].create({"name": "Test product"})
        self.bom = self.env["mrp.bom"].create(
            {
                "product_id": self.product.id,
                "product_tmpl_id": self.product.product_tmpl_id.id,
            }
        )
        self.production = self.env["mrp.production"].create(
            {
                "product_id": self.product.id,
                "analytic_account_id": self.analytic_account.id,
                "product_uom_id": self.product.uom_id.id,
                "bom_id": self.bom.id,
            }
        )

    def test_num_productions(self):
        self.assertEqual(self.analytic_account.num_productions, 1)
