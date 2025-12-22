from odoo import models, fields, api, _


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.onchange("team_id")
    def _onchange_account_distribution(self):
        if self.invoice_count >= 1:
            return {
                "warning": {
                    "title": _("Warning"),
                    "message": _(
                        "You are changing the Sales Team while an invoice already exists. you must update the analytic distribution manually in invoice."
                    ),
                }
            }
        else:
            return {}


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.depends("order_id.partner_id", "product_id", "order_id.team_id")
    def _compute_analytic_distribution(self):
        for line in self:
            if not line.display_type:
                distribution = line.env[
                    "account.analytic.distribution.model"
                ]._get_distribution(
                    {
                        "product_id": line.product_id.id,
                        "product_categ_id": line.product_id.categ_id.id,
                        "partner_id": line.order_id.partner_id.id,
                        "partner_category_id": line.order_id.partner_id.category_id.ids,
                        "company_id": line.company_id.id,
                        "team_id": line.order_id.team_id.id,  # add team id
                    }
                )
                line.analytic_distribution = distribution or line.analytic_distribution
