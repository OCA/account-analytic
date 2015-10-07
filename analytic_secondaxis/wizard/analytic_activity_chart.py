# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2010 Camptocamp SA (http://www.camptocamp.com)
# Copyright (c) 2015 Taktik SA (http://www.taktik.be)
# All Right Reserved
#
# Author : Joel Grand-guillaume (Camptocamp)
# Author : Adil Houmadi (Taktik)
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

from openerp import models, fields, api


class ActivitiesAnalyticChart(models.TransientModel):
    _name = 'activities.analytic.chart'
    _description = 'Analytic Activities Chart'

    from_date = fields.Date(
        string="From",
        required=False
    )
    to_date = fields.Date(
        string="To",
        required=False
    )

    @api.multi
    def analytic_activities_chart_open_window(self):
        mod_obj = self.env['ir.model.data']
        act_obj = self.env['ir.actions.act_window']
        result_context = {}
        result = mod_obj.get_object_reference(
            'analytic_secondaxis',
            'action_activity_tree'
        )
        rec_id = result and result[1] or False
        result = act_obj.browse(rec_id).read()[0]
        if self.from_date:
            result_context.update(
                {'from_date': self.from_date}
            )
        if self.to_date:
            result_context.update(
                {'to_date': self.to_date}
            )
        result['context'] = str(result_context)
        return result
