# -*- coding: utf-8 -*-
# Copyright 2017 PESOL (http://pesol.es)
#                Luis Adan Jimenez Hernandez (luis.jimenez@pesol.es)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Project Task Analytic Tag",
    "summary": "Analytic tag in project task",
    "version": "10.0.1.0.0",
    "author": "PESOL, Odoo Community Association (OCA)",
    "website": "http://pesol.es",
    "category": "Analytic Accont",
    "license": "AGPL-3",
    "depends": [
        'project',
        "hr_timesheet"
    ],
    "data": [
        'views/project_task_analytic_view.xml',
    ],
    'installable': True,
}
