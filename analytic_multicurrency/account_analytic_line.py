# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2010 Camtocamp SA
# @author Joël Grand-Guillaume
# $Id: $
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

import time

from osv import fields
from osv import osv
from tools.translate import _

from tools import config

class account_analytic_line(osv.osv):
    _inherit = 'account.analytic.line'

    def _amount_currency(self, cr, uid, ids, field_name, arg, context={}):
        result = {}
        for rec in self.browse(cr, uid, ids, context):
            cmp_cur_id=rec.company_id.currency_id.id
            aa_cur_id=rec.account_id.currency_id.id
            # Always provide the amount in currency
            if cmp_cur_id != aa_cur_id:
                cur_obj = self.pool.get('res.currency')
                ctx = {}
                if rec.date and rec.amount:
                    ctx['date'] = rec.date
                    result[rec.id] = cur_obj.compute(cr, uid, rec.company_id.currency_id.id,
                        rec.account_id.currency_id.id, rec.amount,
                        context=ctx)
            else:
                result[rec.id]=rec.amount
        return result
        
    def _get_account_currency(self, cr, uid, ids, field_name, arg, context={}):
        result = {}
        for rec in self.browse(cr, uid, ids, context):
            # Always provide second currency
            result[rec.id] = (rec.account_id.currency_id.id,rec.account_id.currency_id.name)
        return result
    
    def _get_account_line(self, cr, uid, ids, context={}):
        aac_ids = {}
        for acc in self.pool.get('account.analytic.account').browse(cr, uid, ids):
            aac_ids[acc.id] = True
        aal_ids = []
        if aac_ids:
            aal_ids = self.pool.get('account.analytic.line').search(cr, uid, [('account_id','in',aac_ids.keys())], context=context)
        return aal_ids
    # Add the account currency and amount in this currency on each analytic line
    # The company_id of analytic line is always realted to the company of the general account
    # linked on the line
    _columns = {
          'aa_currency_id': fields.function(_get_account_currency, method=True, type='many2one', relation='res.currency', string='Account currency',
                  store={
                      'account.analytic.account': (_get_account_line, ['currency_id','company_id'], 50),
                      'account.analytic.line': (lambda self,cr,uid,ids,c={}: ids, ['amount','unit_amount','product_uom_id'],10),
                  },
                  help="The related analytic account currency."),
          'aa_amount_currency': fields.function(_amount_currency, method=True, digits=(16, int(config['price_accuracy'])), string='Amount currency',
                  store={
                      'account.analytic.account': (_get_account_line, ['currency_id','company_id'], 50),
                      'account.analytic.line': (lambda self,cr,uid,ids,c={}: ids, ['amount','unit_amount','product_uom_id'],10),
                  },
                  help="The amount expressed in the related analytic account currency."),
          'company_id': fields.related('general_account_id', 'company_id', type='many2one', relation='res.company', string='Company', store=True, readonly=True),
    }

    # property_valuation_price_type property
    def on_change_unit_amount(self, cr, uid, id, prod_id, quantity, company_id,
            unit=False, journal_id=False, context=None):
        if context==None:
            context={}
        company_obj=self.pool.get('res.company')
        context['currency_id']=company_obj.browse(cr,uid,company_id).currency_id.id
        res=super(account_analytic_line,self).on_change_unit_amount(cr, uid, id, prod_id, quantity, company_id, \
                unit=unit, journal_id=journal_id, context=context)
        return res
        
        
account_analytic_line()