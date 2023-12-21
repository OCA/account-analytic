# Copyright (C) 2019 Open Source Integrators
# Copyright 2023 Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestStockScrap(TransactionCase):
    def setUp(self):
        super().setUp()

        self.product = self.env.ref("product.product_product_4")
        self.warehouse = self.env.ref("stock.warehouse0")
        self.location = self.warehouse.lot_stock_id
        self.analytic_distribution = dict(
            {str(self.env.ref("analytic.analytic_agrolait").id): 100.0}
        )
        # analytic.analytic_agrolait belongs to analytic.analytic_plan_projects
        self.analytic_applicability = self.env["account.analytic.applicability"].create(
            {
                "business_domain": "stock_move",
                "applicability": "optional",
                "analytic_plan_id": self.env.ref("analytic.analytic_plan_projects").id,
            }
        )

    def __update_qty_on_hand_product(self, product, new_qty):
        qty_wizard = self.env["stock.change.product.qty"].create(
            {
                "product_id": product.id,
                "product_tmpl_id": product.product_tmpl_id.id,
                "new_quantity": new_qty,
            }
        )
        qty_wizard.change_product_qty()

    def _create_scrap(self, analytic_distribution=False):
        scrap_data = {
            "product_id": self.product.id,
            "scrap_qty": 1.00,
            "product_uom_id": self.product.uom_id.id,
            "location_id": self.location.id,
            "analytic_distribution": analytic_distribution or False,
        }
        return self.env["stock.scrap"].create(scrap_data)

    def _validate_scrap_no_error(self, scrap):
        scrap.action_validate()
        self.assertEqual(scrap.state, "done")

    def _check_analytic_distribution_no_error(self, scrap):
        domain = [("name", "=", scrap.name)]
        acc_lines = self.env["account.move.line"].search(domain)
        for acc_line in acc_lines:
            if (
                acc_line.account_id
                != scrap.product_id.categ_id.property_stock_valuation_account_id
            ):
                self.assertEqual(
                    acc_line.analytic_distribution, scrap.analytic_distribution
                )

    def test_scrap_without_analytic_optional(self):
        self.__update_qty_on_hand_product(self.product, 1)
        scrap = self._create_scrap()
        self._validate_scrap_no_error(scrap)

    def test_scrap_without_analytic_mandatory(self):
        self.analytic_applicability.write({"applicability": "mandatory"})
        self.__update_qty_on_hand_product(self.product, 1)
        scrap = self._create_scrap()
        with self.assertRaises(ValidationError):
            self._validate_scrap_no_error(scrap)

    def test_scrap_with_analytic(self):
        self.__update_qty_on_hand_product(self.product, 1)
        scrap = self._create_scrap(
            self.analytic_distribution,
        )
        self._validate_scrap_no_error(scrap)
        self._check_analytic_distribution_no_error(scrap)
