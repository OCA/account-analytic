# Copyright 2016 Carlos Dauden <carlos.dauden@tecnativa.com>
# Copyright 2017 Vicent Cubells <vicent.cubells@tecnativa.com>
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


class PurchaseAnalyticCommon:
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.procurement_group_obj = cls.env["procurement.group"]
        cls.product = cls.env.ref("product.product_product_8")
        cls.analytic_account = cls.env["account.analytic.account"].create(
            {
                "name": "Test Analytic Account",
            }
        )
        cls.buy_rule = cls.env["stock.rule"].search(
            [
                ("action", "=", "buy"),
                ("warehouse_id", "=", cls.env.ref("stock.warehouse0").id),
            ]
        )
        extra_values = {
            "route_ids": cls.buy_rule.route_id,
        }
        cls.procur_vals = [
            cls.env["procurement.group"].Procurement(
                cls.product,
                1.0,
                cls.product.uom_id,
                cls.env.ref("stock.warehouse0").lot_stock_id,
                "/",
                "/",
                cls.env.company,
                extra_values,
            )
        ]
        extra_values_2 = extra_values.copy()
        extra_values_2["analytic_account_id"] = cls.analytic_account.id
        cls.procur_vals_2 = [
            cls.env["procurement.group"].Procurement(
                cls.product,
                2.0,
                cls.product.uom_id,
                cls.env.ref("stock.warehouse0").lot_stock_id,
                "/",
                "/",
                cls.env.company,
                extra_values_2,
            )
        ]
