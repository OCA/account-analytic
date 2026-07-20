# Copyright 2017 ForgeFlow S.L.
# Copyright 2017 Luxim d.o.o.
# Copyright 2017 Matmoz d.o.o.
# Copyright 2017 Deneroteam.
# Copyright 2017 Serpent Consulting Services Pvt. Ltd.
# Copyright 2018 Brainbean Apps
# Copyright 2019 Pesol
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models
from odoo.exceptions import UserError


class AccountAnalyticAccount(models.Model):
    _inherit = "account.analytic.account"
    _parent_name = "parent_id"
    _parent_store = True
    _order = "complete_name"

    parent_path = fields.Char(index=True)
    parent_id = fields.Many2one(
        string="Parent Analytic Account",
        comodel_name="account.analytic.account",
        index=True,
        ondelete="cascade",
    )
    child_ids = fields.One2many(
        string="Child Accounts",
        comodel_name="account.analytic.account",
        inverse_name="parent_id",
        copy=True,
    )
    complete_name = fields.Char(
        compute="_compute_complete_name", recursive=True, store=True
    )

    @api.depends("child_ids.line_ids.amount")
    def _compute_debit_credit_balance(self):
        """
        Warning, this method overwrites the standard because the hierarchy
        of analytic account changes
        """
        res = super()._compute_debit_credit_balance()

        domain = [("company_id", "in", [False] + self.env.companies.ids)]
        if self.env.context.get("from_date", False):
            domain.append(("date", ">=", self.env.context["from_date"]))
        if self.env.context.get("to_date", False):
            domain.append(("date", "<=", self.env.context["to_date"]))

        AccountAnalyticLine = self.env["account.analytic.line"]
        company = self.env.user.company_id
        today = fields.Date.today()

        def _sum_in_company_currency(domain):
            return sum(
                currency._convert(amount_sum, company.currency_id, company, today)
                for currency, amount_sum in AccountAnalyticLine._read_group(
                    domain=domain,
                    groupby=["currency_id"],
                    aggregates=["amount:sum"],
                )
            )

        # Re-compute only accounts with children
        for plan, accounts in self.grouped("plan_id").items():
            for account in accounts.filtered("child_ids"):
                domain += [(plan._column_name(), "child_of", account.id)]
                credit = _sum_in_company_currency(domain + [("amount", ">=", 0.0)])
                debit = _sum_in_company_currency(domain + [("amount", "<", 0.0)])

                account.debit = abs(debit)
                account.credit = credit
                account.balance = account.credit - account.debit
        return res

    @api.constrains("parent_id")
    def check_recursion(self):
        if self._has_cycle():
            raise UserError(
                self.env._("You can not create recursive analytic accounts.")
            )
        return True

    @api.onchange("parent_id")
    def _onchange_parent_id(self):
        for account in self:
            account.partner_id = account.parent_id.partner_id

    @api.depends("name", "parent_id.complete_name")
    def _compute_complete_name(self):
        for account in self:
            if account.parent_id:
                account.complete_name = self.env._(
                    "%(parent)s / %(own)s",
                    parent=account.parent_id.complete_name,
                    own=account.name,
                )
            else:
                account.complete_name = account.name

    @api.constrains("active")
    def check_parent_active(self):
        for account in self.filtered(
            lambda a: a.active
            and a.parent_id
            and a.parent_id not in self
            and not a.parent_id.active
        ):
            raise UserError(
                self.env._(
                    "Please activate first parent account %s",
                    account.parent_id.complete_name,
                )
            )

    @api.depends("complete_name", "code", "partner_id.commercial_partner_id.name")
    def _compute_display_name(self):
        for analytic in self:
            name = analytic.complete_name
            if analytic.code:
                name = f"[{analytic.code}] {name}"
            if analytic.partner_id:
                name = self.env._(
                    "%(name)s - %(partner)s",
                    name=name,
                    partner=analytic.partner_id.commercial_partner_id.name,
                )
            analytic.display_name = name

    def write(self, vals):
        if self and "active" in vals and not vals["active"]:
            self.mapped("child_ids").write({"active": False})
        return super().write(vals)
