# Copyright 2026 - TODAY, Cristiano Mafra Junior <cristiano.mafra@escodoo.com.br>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import _, api, fields, models
from odoo.tools.misc import formatLang


class AnalyticMixin(models.AbstractModel):
    _inherit = "analytic.mixin"

    analytic_distribution_display = fields.Char(
        string="Analytic Distribution (text)",
        compute="_compute_analytic_distribution_display",
        compute_sudo=True,
        help="Human readable version of the analytic_distribution JSON field, "
        "usable in exports, list views and reports.",
    )

    @api.model
    def _analytic_distribution_display_account_ids(self, key):
        """Return the analytic account ids encoded in an analytic_distribution key.

        In 16.0 a key is a single analytic account id (e.g. "218"). Starting
        with 17.0 a key can combine several analytic plans as a comma
        separated list of ids (e.g. "218,45"). Non numeric parts are ignored
        so corrupted data does not break the computation.
        """
        return [int(part) for part in str(key).split(",") if part.strip().isdigit()]

    @api.depends("analytic_distribution")
    def _compute_analytic_distribution_display(self):
        all_account_ids = set()
        for record in self:
            for key in record.analytic_distribution or {}:
                all_account_ids.update(
                    record._analytic_distribution_display_account_ids(key)
                )
        accounts = (
            self.env["account.analytic.account"]
            .with_context(active_test=False)
            .browse(all_account_ids)
            .exists()
        )
        account_names = {account.id: account.display_name for account in accounts}
        for record in self:
            record.analytic_distribution_display = (
                record._get_analytic_distribution_display(account_names)
            )

    def _get_analytic_distribution_display(self, account_names):
        self.ensure_one()
        if not self.analytic_distribution:
            return False
        parts = []
        for key, percentage in self.analytic_distribution.items():
            account_ids = self._analytic_distribution_display_account_ids(key)
            if not account_ids:
                continue
            label = " + ".join(
                account_names.get(account_id, _("ID %s") % account_id)
                for account_id in account_ids
            )
            parts.append((percentage or 0.0, label))
        if not parts:
            return False
        parts.sort(key=lambda part: (-part[0], part[1]))
        return " | ".join(
            "%s (%s%%)"
            % (label, formatLang(self.env, percentage, dp="Percentage Analytic"))
            for percentage, label in parts
        )
