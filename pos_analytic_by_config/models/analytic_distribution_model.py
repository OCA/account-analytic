# Copyright 2020 Tecnativa - David Vidal
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class AccountAnalyticDistributionModel(models.Model):
    _inherit = "account.analytic.distribution.model"

    pos_config_id = fields.Many2one(
        comodel_name="pos.config",
        ondelete="cascade",
        help="Select a Point of Sale for which the analytic distribution will be used",
    )

    def _get_distribution(self, vals):
        vals = vals.copy()
        pos_config_id = self.env.context.get("pos_config_id")
        if pos_config_id:
            vals["pos_config_id"] = pos_config_id
        res = super()._get_distribution(vals)
        return res
