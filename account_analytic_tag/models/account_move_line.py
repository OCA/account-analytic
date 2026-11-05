from odoo import fields, models
from odoo.fields import Command


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    analytic_tag_ids = fields.Many2many(
        comodel_name="account.analytic.tag",
        string="Analytic Tags",
        bypass_search_access=True,
    )

    def _prepare_analytic_lines(self):
        """Set tags to the records that have the same or no analytical account."""
        vals = super()._prepare_analytic_lines()
        analytic_tag = self.sudo().analytic_tag_ids
        if analytic_tag:
            for val in vals:
                account_id = val.get("account_id")
                if not account_id:
                    account_field_name = next(
                        (key for key in val.keys() if key.startswith("x_plan")), None
                    )
                    account_id = val.get(account_field_name)
                tags = analytic_tag.filtered(
                    lambda x, account_id=account_id: (
                        not x.account_analytic_id
                        or x.account_analytic_id.id == account_id
                    )
                )
                val.update({"tag_ids": [Command.set(tags.ids)]})
        return vals
