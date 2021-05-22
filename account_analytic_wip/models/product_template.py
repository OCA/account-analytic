# Copyright (C) 2021 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    def _get_product_accounts(self):
        """
        Add the Variance account, used to post WIP amount exceeding the expected.
        The "Consumed" account (credited) is the stock_input,
        and the "WIP" account (debited) is the sock_valuation account.
        """
        self.ensure_one()
        accounts = super()._get_product_accounts()
        accounts.update(
            {
                "stock_variance": self.categ_id.property_variance_account_id or False,
            }
        )
        return accounts

    def get_product_accounts(self, fiscal_pos=None):
        """
        Add the journal to use for WIP journal entries, 'wip_journal'
        """
        self.ensure_one()
        accounts = super().get_product_accounts(fiscal_pos=fiscal_pos)
        accounts.update({"wip_journal": self.categ_id.property_wip_journal_id or False})
        return accounts
