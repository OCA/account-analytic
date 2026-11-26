# Copyright 2026 Heliconia Solutions Pvt. Ltd.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from itertools import chain
from typing import Any

from odoo import _, api, models, tools

from odoo.addons.report_xlsx_helper.report.report_xlsx_abstract import (
    ReportXlsxAbstract,
)
from odoo.addons.report_xlsx_helper.report.report_xlsx_format import (
    FORMATS,
)

_render = ReportXlsxAbstract._render


class AccountAnalyticLine(models.Model):
    _inherit = "account.analytic.line"

    def button_open_journal_entry(self) -> dict[str, Any] | bool:
        self.ensure_one()
        move = self.move_line_id.move_id
        if not move:
            return False
        return {
            "name": _("Journal Entry"),
            "type": "ir.actions.act_window",
            "res_model": "account.move",
            "context": {"create": False},
            "view_mode": "form",
            "res_id": move.id,
        }

    @api.model
    @tools.ormcache_context(keys=("uid", "studio", "lang", "allowed_company_ids"))
    def _get_cached_analytic_plan_columns(self) -> tuple[tuple[int, str, str], ...]:
        """Return plan metadata cached per user/context."""
        if self.env.context.get("studio"):
            return ()
        plan_model = self.env["account.analytic.plan"]
        if not plan_model.has_access("read"):
            return ()
        project_plans, other_plans = plan_model._get_all_plans()
        return tuple(
            (
                plan.id,
                plan._column_name(),
                plan.display_name,
            )
            for plan in chain(project_plans, other_plans)
        )

    @api.model
    def _clear_analytic_plan_cache(self) -> None:
        self.env.registry.clear_cache()

    def _get_analytic_columns_data(self) -> list[dict[str, Any]]:
        cached_columns = self._get_cached_analytic_plan_columns()
        if not cached_columns:
            return []
        return [
            {
                "plan_id": plan_id,
                "column_name": column_name,
                "plan_name": plan_name,
            }
            for plan_id, column_name, plan_name in cached_columns
        ]

    @api.model
    def _report_xlsx_fields(self) -> list[str]:
        analytic_columns = self._get_analytic_columns_data()
        res = [
            "move_line_id",
            "general_account_id",
            "name",
            "date",
            "ref",
            "partner",
            *(column["column_name"] for column in analytic_columns),
            "product_id",
            "unit_amount",
            "product_uom_id",
            "tag_ids",
            "amount",
        ]
        return res

    @api.model
    def _report_xlsx_template(self) -> dict[str, Any]:
        template = {}
        for column in self._get_analytic_columns_data():
            column_name = column["column_name"]
            template[column_name] = {
                "header": {
                    "value": column["plan_name"],
                    "format": FORMATS["format_theader_yellow_center"],
                },
                "lines": {"value": _render(column_name)},
                "width": 24,
            }
        return template
