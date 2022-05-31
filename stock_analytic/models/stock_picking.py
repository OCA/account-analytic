from odoo import models, fields, api


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    picking_type_analytic_account_id = fields.Many2one(related='picking_type_id.analytic_account_id')

    @api.onchange('picking_type_analytic_account_id', 'move_ids_without_package', 'move_lines')
    def _set_analytic_account(self):
        for picking in self:
            (picking.move_lines + picking.move_ids_without_package).write({
                'analytic_account_id': picking.picking_type_analytic_account_id.id
            })


class StockPickingType(models.Model):
    _inherit = 'stock.picking.type'

    analytic_account_id = fields.Many2one('account.analytic.account', 'Analytic Account')
