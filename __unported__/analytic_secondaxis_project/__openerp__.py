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

{
    "name": "Project Analytic Second Axis",
    "version": "1.0",
    "author": "Camptocamp,Odoo Community Association (OCA)",
    "category": "Generic Modules/Accounting",
    "description":
    """
    Add a second analytical axis on analytic lines allowing you to make
    reporting on.

    Unless the account_analytic_plans from OpenERP SA, this module allow you to
    make cross-reporting between those two axes, like all analytic lines that
    concern for example : The activity "Communication" and the project "Product
    1 Integration".

    This second axis is called "activities" and you will be able to define for
    each analytical account, what are the allowed activities for it.

    This module enables the second axis on projet.

    """,
    "website": "http://camptocamp.com",
    "license": "AGPL-3",
    "depends": ["analytic_secondaxis_timesheet",
                "project",
                "project_timesheet",
                ],
    "init_xml": ["security/ir.model.access.csv"],
    "demo_xml": [],
    "update_xml": [
        "analytic_secondaxis_view.xml",
    ],
    "active": False,
    "installable": False
}
