# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


class AccountPaymentCounterpartLine(models.Model):
    _inherit = "account.payment.counterpart.line"

    @api.depends("payment_id.analytic_distribution")
    def _compute_analytic_distribution(self):
        """Fall back to the payment distribution when the line has none.
        The line keeps its own distribution when it is set; otherwise it
        inherits the one from the payment header.
        """
        res = super()._compute_analytic_distribution()
        for line in self:
            if not line.analytic_distribution and line.payment_id.analytic_distribution:
                line.analytic_distribution = line.payment_id.analytic_distribution
        return res
