from odoo import exceptions
from odoo.tests import common


class TestAnalytic(common.TransactionCase):
    def setUp(self):
        super().setUp()
        self.analytic_x = self.env["account.analytic.account"].create(
            {"name": "Analytic X"}
        )
        self.wip_journal = self.env["account.journal"].create(
            {"name": "Inventory WIP", "type": "general", "code": "WIP"}
        )
        self.consume_account = self.env["account.account"].create(
            {
                "code": "600010",
                "name": "Costing Consumed",
                "user_type_id": self.env.ref("account.data_account_type_expenses").id,
            }
        )
        self.wip_account = self.consume_account.copy(
            {"code": "600011", "name": "Costing WIP"}
        )
        self.variance_account = self.consume_account.copy(
            {"code": "600012", "name": "Costing Variance"}
        )
        self.costing_categ = self.env["product.category"].create(
            {
                "name": "Costing",
                "property_cost_method": "standard",
                "property_valuation": "real_time",
                "property_cost_wip_journal_id": self.wip_journal.id,
                "property_cost_consume_account_id": self.consume_account.id,
                "property_cost_wip_account_id": self.wip_account.id,
                "property_cost_variance_account_id": self.variance_account.id,
            }
        )
        self.cost_product_template = self.env["product.template"].create(
            {
                "name": "Cost Service",
                "type": "service",
                "categ_id": self.costing_categ.id,
            }
        )
        self.cost_product = self.cost_product_template.product_variant_ids.write(
            {"standard_price": 10.0}
        )

    def test_100_categ_config_complete(self):
        with self.assertRaises(exceptions.ValidationError):
            self.env["product.category"].create(
                {
                    "name": "Costing",
                    "property_cost_method": "standard",
                    "property_valuation": "real_time",
                    "property_cost_wip_account_id": self.wip_account.id,
                }
            )
