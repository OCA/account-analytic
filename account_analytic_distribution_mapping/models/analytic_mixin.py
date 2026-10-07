# Copyright 2026 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


class AnalyticMixin(models.AbstractModel):
    _inherit = "analytic.mixin"

    @api.model
    def _expand_analytic_distribution(self, distribution):
        if not distribution:
            return distribution
        acc_ids = set()
        for key in distribution:
            acc_ids.update(int(part) for part in str(key).split(",") if part.isdigit())
        if not acc_ids:
            return distribution
        account_model = self.env["account.analytic.account"]
        mapped = {
            account.id: account.mapped_account_ids
            for account in account_model.browse(acc_ids)
        }
        if not any(mapped.values()):
            return distribution
        new_distribution = {}
        changed = False
        for key, percentage in distribution.items():
            line_ids = [int(part) for part in str(key).split(",") if part.isdigit()]
            present_plans = set(account_model.browse(line_ids).root_plan_id.ids)
            extra_ids = []
            for account_id in line_ids:
                for dest in mapped.get(account_id, account_model):
                    dest_plan = dest.root_plan_id
                    if dest_plan.id in present_plans:
                        continue
                    if dest_plan.default_applicability == "unavailable":
                        continue
                    present_plans.add(dest_plan.id)
                    extra_ids.append(dest.id)
            if extra_ids:
                changed = True
            new_key = ",".join(str(_id) for _id in line_ids + extra_ids)
            new_distribution[new_key] = percentage
        return new_distribution if changed else distribution

    def _add_analytic_distribution_mapping(self, vals):
        skip = self.env.context.get("skip_analytic_distribution_mapping")
        if vals.get("analytic_distribution") and not skip:
            vals = dict(vals)
            expand = self._expand_analytic_distribution(vals["analytic_distribution"])
            vals["analytic_distribution"] = expand
        return vals

    @api.model_create_multi
    def create(self, vals_list):
        vals_list = [self._add_analytic_distribution_mapping(v) for v in vals_list]
        return super().create(vals_list)

    def write(self, vals):
        return super().write(self._add_analytic_distribution_mapping(vals))

    @api.onchange("analytic_distribution")
    def _onchange_analytic_distribution_mapping(self):
        skip = self.env.context.get("skip_analytic_distribution_mapping")
        if self.analytic_distribution and not skip:
            expanded = self._expand_analytic_distribution(self.analytic_distribution)
            if expanded != self.analytic_distribution:
                self.analytic_distribution = expanded
