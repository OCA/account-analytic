# Copyright (C) 2021 Open Source Integrators
# Copyright (C) 2024 Updated for Odoo 19
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import models


class StockMove(models.Model):
    _inherit = "stock.move"

    def _get_analytic_distribution(self):
        """
        Return the analytic distribution from the production order.
        In Odoo 19, analytic_distribution is a JSON field with format:
        {analytic_account_id: percentage} e.g., {"10": 100.0}
        """
        distribution = super()._get_analytic_distribution()
        if distribution:
            return distribution

        # Get analytic account from production order
        analytic = (
            self.raw_material_production_id.analytic_account_id
            or self.production_id.analytic_account_id
        )
        if analytic:
            return {str(analytic.id): 100.0}
        return distribution
