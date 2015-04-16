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


class ProjectWork(models.Model):
    _inherit = "project.task.work"

    @api.model
    def create(self, values):
        res = super(ProjectWork, self).create(values)
        if 'activity' in values:
            timesheet_obj = self.env['hr.analytic.timesheet']
            timesheet_id = self.hr_analytic_timesheet_id.id
            timesheet = timesheet_obj.browe(timesheet_id)
            timesheet.write({
                'activity': values['activity']
            })
        return res

    @api.multi
    def write(self, values):
        res = super(ProjectWork, self).create(values)
        timesheet_obj = self.env['hr.analytic.timesheet']
        for task in self:
            timesheet_id = task.hr_analytic_timesheet_id.id
            timesheet = timesheet_obj.browe(timesheet_id)
            timesheet.write({
                'activity': task.activity.id
            })
        return res

    activity = fields.Many2one(
        comodel_name="project.activity_al",
        string="Activity",
    )


class ProjectActivityAl(models.Model):
    _inherit = "project.activity_al"

    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        """Check if we are from project.task.work, if yes, look into the
        related analytic account of the project."""
        if self._context.get('from_task', False):
            if self._context.get('project_id', False):
                project_obj = self.pool.get('project.project')
                project = project_obj.browse(
                    self._context.get('project_id')
                ).analytic_account_id.id
                analytic_id = project.analytic_account_id.id
                self._context.update({
                    'account_id': analytic_id,
                    'from_task': False
                })
        return super(ProjectActivityAl, self).search(
            args,
            offset=offset,
            limit=limit,
            order=order,
            count=count
        )
