from odoo import models


class MaintenanceEquipment(models.Model):
    _name = "maintenance.equipment"
    _inherit = ["maintenance.equipment", "analytic.mixin"]
