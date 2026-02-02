# Copyright (C) 2021 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import models


class StockMove(models.Model):
    _inherit = "stock.move"

    def _generate_valuation_lines_data(
        self,
        partner_id,
        qty,
        debit_value,
        credit_value,
        debit_account_id,
        credit_account_id,
        description,
    ):
        """
        Ensure Analytic Account is set on the journal items.
        Self is a singleton.
        """
        rslt = super()._generate_valuation_lines_data(
            partner_id,
            qty,
            debit_value,
            credit_value,
            debit_account_id,
            credit_account_id,
            description,
        )
        analytic = (
            self.raw_material_production_id.analytic_account_id
            or self.production_id.analytic_account_id
        )
        for entry in rslt.values():
            if not entry.get("analytic_account_id") and analytic:
                entry["analytic_account_id"] = analytic.id
        return rslt
