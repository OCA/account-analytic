# Copyright 2024 (APSL - Nagarro) Bernat Obrador
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.tools import frozendict


class AccountMoveLine(models.Model):
    _inherit = ["account.move.line"]

    distribution_model_id = fields.Many2one(
        "account.analytic.distribution.model",
        string="Distribution Model",
    )

    @api.model_create_multi
    def create(self, vals_list):
        res = super().create(vals_list)
        for line in res:
            line._get_distribution_id()
        return res

    def write(self, vals):
        res = super().write(vals)
        if vals.get("account_id") or vals.get("partner_id") or vals.get("product_id"):
            for line in self:
                line._get_distribution_id()
        return res

    @api.depends("account_id", "partner_id", "product_id")
    def _compute_analytic_distribution(self):
        cache = {}

        for line in self:
            if line.display_type == "product" or not line.move_id.is_invoice(
                include_receipts=True
            ):
                arguments = frozendict(
                    {
                        "product_id": line.product_id.id,
                        "product_categ_id": line.product_id.categ_id.id,
                        "partner_id": line.partner_id.id,
                        "partner_category_id": line.partner_id.category_id.ids,
                        "account_prefix": line.account_id.code,
                        "company_id": line.company_id.id,
                        "date": self._get_date(line).strftime("%Y-%m-%d"),
                    }
                )
                if arguments not in cache:
                    cache[arguments] = self.env[
                        "account.analytic.distribution.model"
                    ]._get_distribution(arguments)
                line.analytic_distribution = (
                    cache[arguments] or line.analytic_distribution
                )

    def _get_date(self, line):
        return line.invoice_date or line.move_id.date or fields.Date.today()

    def _get_distribution_id(self):
        """
        Function to assign from wich distribution model we get the
        analytic distribution.
        It's needed, because in _compute_analytic_distribution the line object
        it's a new Id, so we cannot assign related fields.
        """
        self.ensure_one()
        model_obj = self.env["account.analytic.distribution.model"].with_context(
            get_distributiion_model_id=True
        )

        args = frozendict(
            {
                "product_id": self.product_id.id,
                "product_categ_id": self.product_id.categ_id.id,
                "partner_id": self.partner_id.id,
                "partner_category_id": self.partner_id.category_id.ids,
                "account_prefix": self.account_id.code,
                "company_id": self.company_id.id,
                "date": self._get_date(self).strftime("%Y-%m-%d"),
            }
        )

        model = model_obj._get_distribution(args)
        self.distribution_model_id = model.id if model else False
