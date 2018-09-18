# -*- coding: utf-8 -*-
# Copyright 2017 PESOL (http://pesol.es)
#                Angel Moya (angel.moya@pesol.es)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestProjectTask(TransactionCase):

    def setUp(self, *args, **kwargs):
        super(TestProjectTask, self).setUp(*args, **kwargs)

        self.project = self.env.ref(
            'project.project_project_1')

    def test_create_analytic_line(self):
        """Test analytic line creation on project task
        """
        self.project.write({
            'timesheet_ids': [(0, 0, {
                'name': 'test',
                'tag_ids': [(0, 0, {'name': 'name'})]
            })],
        })
