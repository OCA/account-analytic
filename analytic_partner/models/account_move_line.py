<<<<<<< HEAD
=======
# -*- coding: utf-8 -*-
>>>>>>> 4040b305 ([MIG] analytic_account: Migrated to 10.0)
# Copyright 2015 Tecnativa - Pedro M. Baeza
# Copyright 2017 Tecnativa - Luis Martínez
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

<<<<<<< HEAD
from odoo import models
=======
from odoo import api, models
>>>>>>> 4040b305 ([MIG] analytic_account: Migrated to 10.0)


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

<<<<<<< HEAD
    def _prepare_analytic_distribution_line(
        self, distribution, account_id, distribution_on_each_plan
    ):
        vals = super()._prepare_analytic_distribution_line(
            distribution, account_id, distribution_on_each_plan
        )
        vals["other_partner_id"] = self.move_id.partner_id.commercial_partner_id.id
        return vals
=======
    @api.multi
    def _prepare_analytic_line(self):
        res = super(AccountMoveLine, self)._prepare_analytic_line()
        res[0]["other_partner_id"] = self.invoice_id.partner_id.commercial_partner_id.id
        return res
>>>>>>> 4040b305 ([MIG] analytic_account: Migrated to 10.0)
