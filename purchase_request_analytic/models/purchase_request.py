# Copyright 2019 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class PurchaseRequest(models.Model):
    _inherit = 'purchase.request'

    analytic_account_id2 = fields.Many2one(
        comodel_name='account.analytic.account',
        help='Use to store the value of analytic_account if there is no lines')
    analytic_account_id = fields.Many2one(
        compute='_compute_analytic_account_id',
        inverse='_inverse_analytic_account_id',
        comodel_name='account.analytic.account',
        string='Analytic Account', readonly=True,
        states={'draft': [('readonly', False)]},
        store=True,
        help="The analytic account related to a sales order.")

    @api.multi
    @api.depends('line_ids.analytic_account_id')
    def _compute_analytic_account_id(self):
        """ If all purchase request lines have same analytic account set
            analytic_account_id
        """
        for pr in self:
            al = pr.analytic_account_id2
            if pr.line_ids:
                al = pr.line_ids[0].analytic_account_id or False
                for prl in pr.line_ids:
                    if prl.analytic_account_id != al:
                        al = False
                        break
            pr.analytic_account_id = al

    @api.multi
    def _inverse_analytic_account_id(self):
        """ If analytic_account is set on PR, propagate it to all purchase
            request lines
        """
        for pr in self:
            if pr.analytic_account_id:
                pr.line_ids.write({
                    'analytic_account_id': pr.analytic_account_id.id
                })
            pr.analytic_account_id2 = pr.analytic_account_id

    @api.onchange('analytic_account_id')
    def _onchange_analytic_account_id(self):
        """ When analytic_account_id is changed, set analytic account on all
            purchase request lines.
            Do it in one operation to avoid to recompute the
            analytic_account_id field during the change.
            In case of new record, nothing is recomputed to avoid ugly message
        """
        res = []
        for prl in self.line_ids:
            if isinstance(prl.id, int):
                res.append((1, prl.id, {
                    'analytic_account_id': self.analytic_account_id.id
                }))
            else:
                # this is new record, do nothing !
                return
        self.analytic_account_id2 = self.analytic_account_id
        self.line_ids = res
