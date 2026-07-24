from odoo import fields, models


class MaintenanceEquipment(models.Model):
    _inherit = "maintenance.equipment"

    analytic_distribution = fields.Json(
        copy=True,
        default=dict,
    )

    def _get_analytic_distribution(self):
        self.ensure_one()
        return self.analytic_distribution or {}
