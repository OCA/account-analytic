# Copyright 2025 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import Command, api, fields, models


class AnalyticAccountRelationLine(models.Model):
    _name = "analytic.account.relation.line"
    _description = "Analytic Account Relation Line"

    account_id = fields.Many2one("account.analytic.account", ondelete="cascade")
    plan_id = fields.Many2one("account.analytic.plan", required=True)
    plan_id_domain = fields.Binary(compute="_compute_plan_id_domain")
    account_ids = fields.Many2many(
        "account.analytic.account", string="Related Accounts"
    )

    @api.depends("account_id")
    def _compute_plan_id_domain(self):
        for rec in self:
            plan_ids = rec.account_id.relation_line_ids.mapped("plan_id")
            rec.plan_id_domain = [("id", "not in", plan_ids.ids)]

    @api.onchange("plan_id")
    def onchange_plan_id(self):
        self.account_ids = False

    def _get_reciprocal_lines(self, account_ids, plan_id):
        return self.search(
            [("account_id", "in", list(account_ids)), ("plan_id", "=", plan_id)],
        )

    def _update_reciprocal_relations(self, old_account_ids=None):
        for line in self:
            current_ids = set(line.account_ids.ids)
            old_ids = set(old_account_ids or [])
            added_ids = current_ids - old_ids
            remove_ids = old_ids - current_ids
            existing_recip_lines = self._get_reciprocal_lines(
                added_ids, line.account_id.plan_id.id
            )
            missing_ids = added_ids - set(existing_recip_lines.account_id.ids)
            if missing_ids:
                self.create(
                    [
                        {
                            "account_id": aid,
                            "plan_id": line.account_id.plan_id.id,
                            "account_ids": [Command.set([line.account_id.id])],
                        }
                        for aid in missing_ids
                    ]
                )
            if existing_recip_lines:
                existing_recip_lines.write(
                    {"account_ids": [Command.link(line.account_id.id)]}
                )
            if remove_ids:
                recip_lines = self._get_reciprocal_lines(
                    remove_ids, line.account_id.plan_id.id
                )
                recip_lines.write({"account_ids": [Command.unlink(line.account_id.id)]})
                recip_lines.filtered(lambda x: not x.account_ids).unlink()

    @api.model
    def create(self, vals):
        res = super().create(vals)
        for record in res:
            record._update_reciprocal_relations()
        return res

    def write(self, vals):
        old_ids_map = {record.id: set(record.account_ids.ids) for record in self}
        res = super().write(vals)
        for record in self:
            record._update_reciprocal_relations(old_account_ids=old_ids_map[record.id])
        return res

    def unlink(self):
        for record in self:
            recip_lines = self._get_reciprocal_lines(
                record.account_ids.ids, record.account_id.plan_id.id
            )
            recip_lines.write({"account_ids": [Command.unlink(record.account_id.id)]})
        return super().unlink()
