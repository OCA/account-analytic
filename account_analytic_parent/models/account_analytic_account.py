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
    level = fields.Integer(
        compute="_compute_level", recursive=True, store=True, aggregator=False
    )

    @api.depends("child_ids", "child_ids.level")
    def _compute_level(self):
        for account in self:
            children = account.child_ids
            account.level = max(children.mapped("level")) + 1 if children else 0

    @api.depends("child_ids.line_ids.amount")
    def _compute_debit_credit_balance(self):
        """
        Warning, this method overwrites the standard because the hierarchy
        of analytic account changes
        """
        res = super()._compute_debit_credit_balance()

        def convert(groups):
            return sum(
                currency_id._convert(
                    from_amount=amount_sum,
                    to_currency=self.env.company.currency_id,
                    company=self.env.company,
                    date=fields.Date.today(),
                )
                for currency_id, amount_sum in groups
                if currency_id
            )

        AccountAnalyticLine = self.env["account.analytic.line"]
        # Same filters as the standard computation
        domain = [("company_id", "in", [False] + self.env.companies.ids)]
        if self.env.context.get("from_date", False):
            domain.append(("date", ">=", self.env.context["from_date"]))
        if self.env.context.get("to_date", False):
            domain.append(("date", "<=", self.env.context["to_date"]))

        # Re-compute only accounts with children
        for account in self:
            if not account.child_ids:
                continue
            credit = debit = 0.0
            descendants = self.search([("id", "child_of", account.id)])
            # Each plan stores its accounts in its own column of the lines
            for plan, accounts in descendants.grouped("plan_id").items():
                if not plan:
                    continue
                plan_domain = domain + [(plan._column_name(), "in", accounts.ids)]
                credit += convert(
                    AccountAnalyticLine._read_group(
                        domain=plan_domain + [("amount", ">=", 0.0)],
                        groupby=["currency_id"],
                        aggregates=["amount:sum"],
                    )
                )
                debit += convert(
                    AccountAnalyticLine._read_group(
                        domain=plan_domain + [("amount", "<", 0.0)],
                        groupby=["currency_id"],
                        aggregates=["amount:sum"],
                    )
                )

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
        for account in self:
            if (
                not account.active
                or not account.parent_id
                or account.parent_id in self
                or account.parent_id.active
            ):
                continue
            raise UserError(
                self.env._(
                    "Please activate first parent account %(parent_name)s",
                    parent_name=account.parent_id.name,
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
