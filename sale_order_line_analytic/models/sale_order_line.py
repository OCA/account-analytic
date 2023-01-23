# Copyright 2023 Ecosoft Co., Ltd (http://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    analytic_account_id = fields.Many2one(
        string="Analytic Account",
        comodel_name="account.analytic.account",
        compute="_compute_analytic_account_id",
        store=True,
        readonly=False,
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",
    )

    @api.depends("order_id")
    def _compute_analytic_account_id(self):
        if self.order_id.analytic_account_id:
            self.analytic_account_id = self.order_id.analytic_account_id

    def _prepare_invoice_line(self, **optional_values):
        res = super()._prepare_invoice_line(**optional_values)
        if self.analytic_account_id and not self.display_type:
            res["analytic_account_id"] = self.analytic_account_id.id
        return res
