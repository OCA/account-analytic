# Copyright (C) 2019 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo.tests.common import TransactionCase


class TestStockScrap(TransactionCase):
    def setUp(self):
        super(TestStockScrap, self).setUp()

        self.product = self.env.ref("product.product_product_4")
        self.warehouse = self.env.ref("stock.warehouse0")
        self.location = self.warehouse.lot_stock_id
        self.analytic_account = self.env.ref("analytic.analytic_agrolait")

    def __update_qty_on_hand_product(self, product, new_qty):
        qty_wizard = self.env["stock.change.product.qty"].create(
            {
                "product_id": product.id,
                "product_tmpl_id": product.product_tmpl_id.id,
                "new_quantity": new_qty,
            }
        )
        qty_wizard.change_product_qty()

    def _create_scrap(self, analytic_account_id=False):
        scrap_data = {
            "product_id": self.product.id,
            "scrap_qty": 1.00,
            "product_uom_id": self.product.uom_id.id,
            "location_id": self.location.id,
            "analytic_account_id": analytic_account_id
            and analytic_account_id.id
            or False,
        }
        return self.env["stock.scrap"].create(scrap_data)

    def _validate_scrap_no_error(self, scrap):
        scrap.action_validate()
        self.assertEqual(scrap.state, "done")

    def _check_analytic_account_no_error(self, scrap):
        domain = [("name", "=", scrap.name)]
        acc_lines = self.env["account.move.line"].search(domain)
        for acc_line in acc_lines:
            if (
                acc_line.account_id
                != scrap.product_id.categ_id.property_stock_valuation_account_id
            ):
                self.assertEqual(
                    acc_line.analytic_account_id.id, scrap.analytic_account_id.id
                )

    def test_scrap_without_analytic(self):
        self.__update_qty_on_hand_product(self.product, 1)
        scrap = self._create_scrap()
        self._validate_scrap_no_error(scrap)

    def test_scrap_with_analytic(self):
        self.__update_qty_on_hand_product(self.product, 1)
        scrap = self._create_scrap(self.analytic_account)
        self._validate_scrap_no_error(scrap)
        self._check_analytic_account_no_error(scrap)
