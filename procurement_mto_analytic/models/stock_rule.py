# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import json

from odoo import models


class StockRule(models.Model):
    _inherit = "stock.rule"

    def _find_matching_analytic_distribution_record(self, analytic_distribution):
        # Prepare the JSONB structure as a string for the SQL query
        analytic_distribution_str = json.dumps(analytic_distribution)
        # Use a parameterized query for safety
        query = """
        SELECT id FROM purchase_order_line
        WHERE analytic_distribution::jsonb = %s::jsonb;
        """
        self.env.cr.execute(query, (analytic_distribution_str,))
        result = self.env.cr.fetchall()
        # Extract IDs from the result
        matching_po_line = [res[0] for res in result]
        return matching_po_line

    def _make_po_get_domain(self, company_id, values, partner):
        domain = super()._make_po_get_domain(company_id, values, partner)
        if values.get("analytic_distribution"):
            # Fetch matching record IDs based on dynamic analytic_distribution
            matching_po_line = self._find_matching_analytic_distribution_record(
                values["analytic_distribution"]
            )
            if matching_po_line:
                domain += (("order_line", "in", tuple(matching_po_line)),)
            else:
                # To create new PO
                domain += (("order_line", "=", 0000000),)
        else:
            domain += (("order_line.analytic_distribution", "=", False),)
        return domain
