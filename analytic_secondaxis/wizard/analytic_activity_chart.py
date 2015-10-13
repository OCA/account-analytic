# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2010 Camptocamp SA (http://www.camptocamp.com)
# All Right Reserved
#
# Author : Joel Grand-guillaume (Camptocamp)
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
from osv import osv, fields


class activities_analytic_chart(osv.osv_memory):
    _name = 'activities.analytic.chart'
    _description = 'Analytic Activities Chart'

    _columns = {
        'from_date': fields.date('From'),
        'to_date': fields.date('To'),
    }

    def analytic_activities_chart_open_window(self, cr, uid, ids,
                                              context=None):
        mod_obj = self.pool.get('ir.model.data')
        act_obj = self.pool.get('ir.actions.act_window')
        result_context = {}
        if context is None:
            context = {}
        result = mod_obj.get_object_reference(cr, uid, 'analytic_secondaxis',
                                              'action_activity_tree')
        rec_id = result and result[1] or False
        result = act_obj.read(cr, uid, [rec_id], context=context)[0]
        data = self.read(cr, uid, ids, [])[0]
        if data['from_date']:
            result_context.update({'from_date': data['from_date']})
        if data['to_date']:
            result_context.update({'to_date': data['to_date']})
        result['context'] = str(result_context)
        return result
