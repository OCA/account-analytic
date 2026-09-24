from odoo import models


class AccountPaymentRegister(models.TransientModel):
    _name = "account.payment.register"
    _inherit = ["account.payment.register", "analytic.mixin"]

    def _create_payment_vals_from_wizard(self, batch_result):
        payment_vals = super()._create_payment_vals_from_wizard(batch_result)
        if self.analytic_distribution:
            payment_vals["analytic_distribution"] = self.analytic_distribution
        return payment_vals
