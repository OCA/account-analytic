# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2014 Serv. Tecnol. Avanzados (http://www.serviciosbaeza.com)
#                       Pedro Manuel Baeza <pedro.baeza@serviciosbaeza.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import fields, orm


class HrExpenseExpense(orm.Model):
    _inherit = 'hr.expense.expense'

    def line_get_convert(self, cr, uid, x, part, date, context=None):
        res = super(HrExpenseExpense, self).line_get_convert(cr, uid, x, part,
                                                             date,
                                                             context=context)
        res['analytics_id'] = x.get('analytics_id', False)
        return res

    def move_line_get_item(self, cr, uid, line, context=None):
        res = super(HrExpenseExpense, self).move_line_get_item(cr, uid, line,
                                                               context=context)
        if line.analytics_id:
            res['analytics_id'] = line.analytics_id.id
        return res


class HrExpenseLine(orm.Model):
    _inherit = 'hr.expense.line'
    _columns = {
        'analytics_id': fields.many2one('account.analytic.plan.instance',
                                        'Analytic distribution'),
    }
