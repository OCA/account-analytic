# Copyright (C) 2021 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import _, api, exceptions, fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    is_cost_type = fields.Boolean()

    def _get_product_accounts(self):
        """
        Add the Variance account, used to post WIP amount exceeding the expected.
        The "Consumed" account (credited) is the stock_input,
        and the "WIP" account (debited) is the sock_valuation account.
        """
        accounts = super()._get_product_accounts()
        accounts.update(
            {"stock_variance": self.categ_id.property_variance_account_id or False}
        )
        return accounts

    def get_product_accounts(self, fiscal_pos=None):
        """
        Add the journal to use for WIP journal entries, 'wip_journal'
        """
        accounts = super().get_product_accounts(fiscal_pos=fiscal_pos)
        accounts.update({"wip_journal": self.categ_id.property_wip_journal_id or False})
        return accounts


class Product(models.Model):
    _inherit = "product.product"

    activity_cost_ids = fields.One2many(
        "activity.cost.rule",
        "parent_id",
        string="Activity Costs",
        help="This product will also generate analytic items for these Activity Costs",
    )

    @api.constrains("is_cost_type", "activity_cost_ids")
    def constrains_is_cost_type(self):
        for product in self:
            if not product.is_cost_type and product.activity_cost_ids:
                raise exceptions.ValidationError(
                    _("Can't have Activity Costs set if it is not a Cost Type.")
                )

    @api.onchange("activity_cost_ids")
    def onchange_for_standard_price(self):
        "Rollup Activity Costs to parent Cost Type"
        for product in self.filtered("is_cost_type").filtered("activity_cost_ids"):
            product.standard_price = sum(
                product.mapped("activity_cost_ids.standard_price")
            )
