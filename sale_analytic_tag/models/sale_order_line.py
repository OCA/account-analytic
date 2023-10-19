# Copyright 2023 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from odoo import fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    analytic_tag_ids = fields.Many2many(
        comodel_name="account.analytic.tag",
        string="Analytic Tags",
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",
    )

    def _prepare_invoice_line(self, **optional_values):
        vals = super()._prepare_invoice_line(**optional_values)
        if self.analytic_tag_ids:
            vals.update({"analytic_tag_ids": [(6, 0, self.analytic_tag_ids.ids)]})
        return vals
