# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class AccountInvoiceLine(models.Model):

    _inherit = 'account.invoice.line'

    @api.model_create_multi
    def create(self, vals_list):
        invoice_model = self.env['account.invoice']
        for vals in vals_list:
            if vals.get('invoice_id'):
                invoice = invoice_model.browse(vals.get('invoice_id'))
                if (
                    invoice
                    and invoice.team_id
                    and invoice.team_id.analytic_tag_ids
                ):
                    if not vals.get('analytic_tag_ids'):
                        vals['analytic_tag_ids'] = []
                    vals['analytic_tag_ids'].extend(
                        [
                            (4, tag.id)
                            for tag in invoice.team_id.analytic_tag_ids
                        ]
                    )
        return super().create(vals_list)
