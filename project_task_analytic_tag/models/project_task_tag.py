# -*- coding: utf-8 -*-
# Copyright 2017 PESOL (http://pesol.es)
#                Luis Adan Jimenez Hernandez (luis.jimenez@pesol.es)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields


class ProjectTaskTag(models.Model):
    _inherit = 'project.task'

    analytic_tag_ids = fields.Many2many(
        comodel_name='account.analytic.tag',
        relation='project_task_analytic_tag_rel',
        column1='analytic_tag_ids',
        column2='default_tag_ids',
        string='Analytic Tag')
