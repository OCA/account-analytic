from odoo import api, fields, models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    analytic_category_ids = fields.Many2many(
        string="Analytic Category",
        comodel_name="account.analytic.category",
        relation="account_move_line_category_rel",
        column1="line_id",
        column2="category_id",
        readonly=True,
        store=True,
        compute="_compute_analytic_category_ids",
        help="The categories of related analytic accounts. Save to update the field.",
    )

    @api.depends("analytic_distribution")
    def _compute_analytic_category_ids(self):
        for line in self:
            line.analytic_category_ids = line.analytic_account_ids.mapped("category_id")
