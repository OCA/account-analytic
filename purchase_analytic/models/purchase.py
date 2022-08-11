# © 2016  Laetitia Gangloff, Acsone SA/NV (http://www.acsone.eu)
# Copyright 2022 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    project_id = fields.Many2one(
        compute="_compute_project_id",
        inverse="_inverse_project_id",
        comodel_name="account.analytic.account",
        string="Analytic Account",
        readonly=True,
        states={"draft": [("readonly", False)]},
        store=True,
        help="The analytic account related to a purchase order.",
    )

    @api.depends("order_line.account_analytic_id")
    def _compute_project_id(self):
        """If all order line have same analytic account set project_id.
        If no lines, respect value given by the user.
        """
        for po in self:
            if po.order_line:
                al = po.order_line[0].account_analytic_id or False
                for ol in po.order_line:
                    if ol.account_analytic_id != al:
                        al = False
                        break
                po.project_id = al

    def _inverse_project_id(self):
        """When set project_id set analytic account on all order lines"""
        for po in self:
            if po.project_id:
                po.order_line.write({"account_analytic_id": po.project_id.id})

    @api.onchange("project_id")
    def _onchange_project_id(self):
        """When change project_id set analytic account on all order lines"""
        if self.project_id:
            self.order_line.update({"account_analytic_id": self.project_id.id})
