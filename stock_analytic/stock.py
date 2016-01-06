# -*- coding: utf-8 -*-
###############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2012 Julius Network Solutions SARL <contact@julius.fr>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################

from openerp.osv import fields, osv


class stock_location(osv.Model):
    _inherit = "stock.location"

    _columns = {
        'account_analytic_in_id': fields.many2one('account.analytic.account',
                                                  'Analytic account (in)'),
        'account_analytic_out_id': fields.many2one('account.analytic.account',
                                                   'Analytic account (out)'),
    }


class stock_quant(osv.Model):

    _inherit = "stock.quant"

    def _account_entry_move(self, cr, uid, quants, move, context=None):
        ctx = context.copy()
        ctx['location_from'] = move.location_id.id
        ctx['location_to'] = quants[0].location_id.id
        super(stock_quant, self)._account_entry_move(
            cr, uid, quants, move, context=ctx)

    def _prepare_account_move_line(
            self, cr, uid, move, qty, cost, credit_account_id,
            debit_account_id, context=None):

        location_obj = self.pool.get('stock.location')
        res = super(stock_quant, self)._prepare_account_move_line(
            cr, uid, move, qty, cost, credit_account_id,
            debit_account_id, context=context)
        location_from_id = context.get('location_from')
        location_to_id = context.get('location_to')
        location_from = location_obj.browse(
            cr, uid, location_from_id, context=context)
        location_to = location_obj.browse(
            cr, uid, location_to_id, context=context)
        if move.location_id.usage not in ('internal', 'transit') and \
                move.location_dest_id.usage == 'internal':
            if location_from and location_from.usage == 'customer':
                # Add analytic account in credit line
                res[1][2].update({
                    'analytic_account_id':
                        move.location_dest_id.account_analytic_in_id.id,
                })
            else:
                # Add analytic account in credit line
                res[1][2].update({
                    'analytic_account_id':
                        move.location_dest_id.account_analytic_out_id.id,
                })
        if move.location_id.usage == 'internal' and \
                move.location_dest_id.usage not in ('internal', 'transit'):
            if location_to and location_to.usage == 'supplier':
                # Add analytic account in debit line
                res[0][2].update({
                    'analytic_account_id':
                        move.location_id.account_analytic_out_id.id,
                })
            else:
                # Add analytic account in credit line
                res[0][2].update({
                    'analytic_account_id':
                        move.location_id.account_analytic_in_id.id,
                })
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
