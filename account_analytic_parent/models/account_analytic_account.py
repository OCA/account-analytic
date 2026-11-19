# Copyright 2017 ForgeFlow S.L.
# Copyright 2017 Luxim d.o.o.
# Copyright 2017 Matmoz d.o.o.
# Copyright 2017 Deneroteam.
# Copyright 2017 Serpent Consulting Services Pvt. Ltd.
# Copyright 2018 Brainbean Apps
# Copyright 2019 Pesol
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from collections import defaultdict

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

        domain = [("company_id", "in", [False] + self.env.companies.ids)]
        if self.env.context.get("from_date"):
            domain.append(("date", ">=", self.env.context["from_date"]))
        if self.env.context.get("to_date"):
            domain.append(("date", "<=", self.env.context["to_date"]))

        AccountAnalyticLine = self.env["account.analytic.line"]
        company = self.env.company
        today = fields.Date.today()

        # Re-compute only accounts with children, each plan uses its own
        # column on analytic lines
        for plan, accounts in self.grouped("plan_id").items():
            parents = accounts.filtered("child_ids")
            if not plan or not parents:
                continue
            column = plan._column_name()
            subtree = self.search([("id", "child_of", parents.ids)])

            # Own credit and debit of every account in the subtrees
            own = defaultdict(lambda: [0.0, 0.0])
            for index, sign_domain in enumerate(
                [[("amount", ">=", 0.0)], [("amount", "<", 0.0)]]
            ):
                for account, currency, amount_sum in AccountAnalyticLine._read_group(
                    domain=domain + [(column, "in", subtree.ids)] + sign_domain,
                    groupby=[column, "currency_id"],
                    aggregates=["amount:sum"],
                ):
                    if currency:
                        own[account.id][index] += currency._convert(
                            amount_sum, company.currency_id, company, today
                        )

            # Add each account's own amounts to itself and its ancestors
            totals = {parent_id: [0.0, 0.0] for parent_id in parents.ids}
            for account in subtree:
                if account.id not in own:
                    continue
                credit, debit = own[account.id]
                for ancestor_id in account.parent_path.split("/")[:-1]:
                    total = totals.get(int(ancestor_id))
                    if total is not None:
                        total[0] += credit
                        total[1] += debit

            for parent in parents:
                credit, debit = totals[parent.id]
                parent.debit = abs(debit)
                parent.credit = credit
                parent.balance = parent.credit - parent.debit
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
