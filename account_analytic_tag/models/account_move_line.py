from odoo import fields, models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    analytic_tag_ids = fields.Many2many(
        comodel_name="account.analytic.tag",
        string="Analytic Tags",
    )

    def _prepare_analytic_lines(self):
        """Set tags to the records that have the same or no analytical account."""
        vals = super()._prepare_analytic_lines()
        if self.analytic_tag_ids:
            for val in vals:
                account_id = [
                    value for key, value in val.items() if key.startswith("x_plan")
                ][0]
                tags = self.analytic_tag_ids.filtered(
                    lambda x, y=account_id: not x.account_analytic_id
                    or x.account_analytic_id.id == y
                )
                val.update({"tag_ids": [(6, 0, tags.ids)]})
        return vals
