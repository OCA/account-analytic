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
                account_id = val.get("account_id")
                if not account_id:
                    account_field_name = next(
                        (key for key in val.keys() if key.startswith("x_plan")), None
                    )
                    account_id = val.get(account_field_name)
                tags = self.analytic_tag_ids.filtered(
                    lambda x, account_id=account_id: (
                        not x.account_analytic_id
                        or x.account_analytic_id.id == account_id
                    )
                )
                val.update({"tag_ids": [(6, 0, tags.ids)]})
        return vals
