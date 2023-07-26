# Copyright 2019 ForgeFlow S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class PurchaseRequest(models.Model):
    _inherit = "purchase.request"

    analytic_account_id = fields.Many2one(
        compute="_compute_analytic_account_id",
        inverse="_inverse_analytic_account_id",
        comodel_name="account.analytic.account",
        string="Analytic Account",
        readonly=True,
        states={"draft": [("readonly", False)]},
        store=True,
        help="The analytic account related to a sales order.",
    )

    @api.depends("line_ids.analytic_account_id")
    def _compute_analytic_account_id(self):
        """If all purchase request lines have same analytic account set
        analytic_account_id
        """
        for pr in self:
            al = pr.analytic_account_id
            if pr.line_ids:
                for prl in pr.line_ids:
                    if prl.analytic_account_id != al:
                        al = False
                        break
            pr.analytic_account_id = al

    def _inverse_analytic_account_id(self):
        """If analytic_account is set on PR, propagate it to all purchase
        request lines
        """
        for pr in self:
            if pr.analytic_account_id:
                for line in pr.line_ids:
                    line.analytic_account_id = pr.analytic_account_id.id
