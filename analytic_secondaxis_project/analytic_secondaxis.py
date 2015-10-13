# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2010 Camptocamp SA (http://www.camptocamp.com)
# All Right Reserved
#
# Author : Joel Grand-guillaume (Camptocamp)
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

from osv import fields
from osv import osv


class project_work(osv.osv):
    _inherit = "project.task.work"
    _columns = {
        'activity': fields.many2one('project.activity_al', 'Activity'),
    }

    def create(self, cr, uid, vals, *args, **kwargs):
        res = super(project_work, self).create(cr, uid, vals, *args, **kwargs)
        if 'activity' in vals:
            context = kwargs.get('context', {})
            task_work_obj = self.pool.get('project.task.work')
            timesheet_obj = self.pool.get('hr.analytic.timesheet')
            hr_ts_line_id = task_work_obj.browse(
                cr, uid, res).hr_analytic_timesheet_id.id
            timesheet_obj.write(cr, uid, [hr_ts_line_id], {
                'activity': vals['activity']
            }, context)
        return res

    def write(self, cr, uid, ids, vals, context=None):
        res = super(project_work, self).write(cr, uid, ids, vals, context)
        task_work_obj = self.pool.get('project.task.work')
        timesheet_obj = self.pool.get('hr.analytic.timesheet')
        for task in self.browse(cr, uid, ids, context=context):
            hr_ts_line_id = task_work_obj.browse(
                cr, uid, task.id).hr_analytic_timesheet_id.id
            timesheet_obj.write(cr, uid, [hr_ts_line_id], {
                'activity': task.activity.id
            }, context)
        return res


class project_activity_al(osv.osv):
    """Class that inhertis osv.osv and add 2nd analytic axe to account analytic
    lines.  The _name is kept for previous version compatibility
    (project.activity_al)."""
    # Keep that name for back -patibility
    _inherit = "project.activity_al"
    _description = "Second Analytical Axes"

    def search(self, cr, uid, args, offset=0, limit=None, order=None,
               context=None, count=False):
        """Check if we are from project.task.work, if yes, look into the
        related analytic account of the project."""

        if context is None:
            context = {}
        if context.get('from_task', False):
            if context.get('project_id', False):
                proj_obj = self.pool.get('project.project')
                analytic_id = proj_obj.browse(
                    cr, uid, context.get('project_id', False)
                ).analytic_account_id.id
                context.update({'account_id': analytic_id, 'from_task': False})

        return super(project_activity_al, self).search(
            cr, uid, args, offset, limit, order, context=context, count=count)
