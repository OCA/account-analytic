# Copyright 2024 (APSL - Nagarro) Bernat Obrador
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.tools import date_utils


class AnalyticTrialBalanceReportWizard(models.TransientModel):
    _name = "ac.trial.balance.report.wizard"
    _description = "Analytic Trial Balance Report Wizard"
    _inherit = "account_analytic_report_abstract_wizard"

    date_range_id = fields.Many2one(comodel_name="date.range", string="Date range")
    date_from = fields.Date(required=True)
    date_to = fields.Date(required=True)
    fy_start_date = fields.Date(compute="_compute_fy_start_date")
    account_ids = fields.Many2many(
        comodel_name="account.analytic.account", string="Filter accounts"
    )
    plan_id = fields.Many2one(
        "account.analytic.plan", domain="[('parent_id', '=', False)]", required=True
    )

    group_by_analytic_account = fields.Boolean(string="Group by Analytic Account")
    show_hierarchy = fields.Boolean(help="Shows hierarchy of the financial accounts")
    limit_hierarchy_level = fields.Boolean(help="Limits hierarchy level")
    hierarchy_level = fields.Integer(help="Hierarchy levels to show", default=1)

    show_months = fields.Boolean(
        help="""
    This option works only when exporting to Excel. It will create a separate sheet
    for each selected analytic account, displaying all financial accounts with a
    balance.
    For each account, it shows the monthly balance within the selected date range.
    """
    )
    account_code_from = fields.Many2one(
        "account.account",
        help="Starting account in a range",
    )
    account_code_to = fields.Many2one(
        "account.account",
        help="Ending account in a range",
    )
    account_account_ids = fields.Many2many(
        "account.account",
        string="Financial Accounts Filter",
    )

    @api.onchange("account_code_from", "account_code_to")
    def on_change_account_range(self):
        Account = self.env["account.account"]
        for rec in self:
            if not rec.account_code_from and not rec.account_code_to:
                rec.account_account_ids = [(6, 0, [])]
                continue

            start_code = rec.account_code_from.code if rec.account_code_from else None
            end_code = rec.account_code_to.code if rec.account_code_to else None

            if start_code and not end_code:
                end_code = start_code
            elif end_code and not start_code:
                start_code = end_code

            if start_code and end_code and start_code > end_code:
                start_code, end_code = end_code, start_code

            domain = [
                ("company_id", "=", rec.company_id.id),
                ("deprecated", "=", False),
            ]
            if start_code and end_code:
                domain += [("code", ">=", start_code), ("code", "<=", end_code)]

            accounts = Account.search(domain, order="code")
            rec.account_account_ids = [(6, 0, accounts.ids)]

    @api.depends("date_from")
    def _compute_fy_start_date(self):
        for wiz in self:
            if wiz.date_from:
                date_from, date_to = date_utils.get_fiscal_year(
                    wiz.date_from,
                    day=self.company_id.fiscalyear_last_day,
                    month=int(self.company_id.fiscalyear_last_month),
                )
                wiz.fy_start_date = date_from
            else:
                wiz.fy_start_date = False

    @api.onchange("company_id")
    def onchange_company_id(self):
        """Handle company change."""
        if (
            self.company_id
            and self.date_range_id.company_id
            and self.date_range_id.company_id != self.company_id
        ):
            self.date_range_id = False

        res = {
            "domain": {
                "date_range_id": [],
            }
        }
        if not self.company_id:
            return res
        else:
            # res["domain"]["account_ids"] += [("company_id", "=", self.company_id.id)]
            res["domain"]["date_range_id"] += [
                "|",
                ("company_id", "=", self.company_id.id),
                ("company_id", "=", False),
            ]
        return res

    @api.onchange("date_range_id")
    def onchange_date_range_id(self):
        """Handle date range change."""
        self.date_from = self.date_range_id.date_start
        self.date_to = self.date_range_id.date_end

    @api.onchange("group_by_analytic_account")
    def onchange_group_by_analytic_account(self):
        if self.group_by_analytic_account:
            self._not_show_hierarchy()

    @api.onchange("plan_id")
    def _onchange_plan_id(self):
        if self.account_ids:
            self.account_ids = False
            self.show_months = False

    @api.constrains("company_id", "date_range_id")
    def _check_company_id_date_range_id(self):
        for rec in self.sudo():
            if (
                rec.company_id
                and rec.date_range_id.company_id
                and rec.company_id != rec.date_range_id.company_id
            ):
                raise ValidationError(
                    _(
                        "The Company in the Trial Balance Report Wizard and in "
                        "Date Range must be the same."
                    )
                )

    @api.constrains("show_hierarchy", "hierarchy_level")
    def _check_show_hierarchy_level(self):
        for rec in self:
            if rec.show_hierarchy and rec.hierarchy_level <= 0:
                raise UserError(
                    _("The hierarchy level to filter on must be greater than 0.")
                )

    @api.onchange("account_ids")
    def _onchange_account_ids(self):
        if self.account_ids:
            self._not_show_hierarchy()

    def _print_report(self, report_type):
        self.ensure_one()
        data = self._prepare_report_trial_balance_analytic()
        if report_type == "xlsx":
            report_name = "a_a_r.report_trial_balance_analytic_xlsx"
        else:
            report_name = "account_analytic_report.trial_balance_analytic"

        return (
            self.env["ir.actions.report"]
            .search(
                [("report_name", "=", report_name), ("report_type", "=", report_type)],
                limit=1,
            )
            .report_action(self, data=data)
        )

    def _not_show_hierarchy(self):
        self.show_hierarchy = False
        self.limit_hierarchy_level = False
        self.hierarchy_level = 1

    def _prepare_report_trial_balance_analytic(self):
        self.ensure_one()
        sorted_accounts_ids = sorted([account.id for account in self.account_ids])
        return {
            "wizard_id": self.id,
            "date_from": self.date_from,
            "date_to": self.date_to,
            "company_id": self.company_id.id,
            "account_ids": sorted_accounts_ids or [],
            "fy_start_date": self.fy_start_date,
            "account_analytic_report_lang": self.env.lang,
            "plan_field": self.plan_id._column_name(),
            "plan_name": self.plan_id.name,
            "plan_id": self.plan_id.id,
            "group_by_analytic_account": self.group_by_analytic_account,
            "show_hierarchy": self.show_hierarchy,
            "limit_hierarchy_level": self.limit_hierarchy_level,
            "hierarchy_level": self.hierarchy_level,
            "show_months": self.show_months,
            "account_account_ids": self.account_account_ids.ids,
        }

    def _export(self, report_type):
        """Default export is PDF."""
        return self._print_report(report_type)
