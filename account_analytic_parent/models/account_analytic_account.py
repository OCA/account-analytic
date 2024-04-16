# Copyright 2017 ForgeFlow S.L.
# Copyright 2017 Luxim d.o.o.
# Copyright 2017 Matmoz d.o.o.
# Copyright 2017 Deneroteam.
# Copyright 2017 Serpent Consulting Services Pvt. Ltd.
# Copyright 2018 Brainbean Apps
# Copyright 2019 Pesol
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
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

        ResCurrency = self.env["res.currency"]
        AccountAnalyticLine = self.env["account.analytic.line"]
        user_currency_id = self.env.user.company_id.currency_id

        # Re-compute only accounts with children
        for account in self.filtered("child_ids"):
            domain = [("account_id", "child_of", account.id)]

            credit_groups = AccountAnalyticLine.read_group(
                domain=domain + [("amount", ">=", 0.0)],
                fields=["currency_id", "amount"],
                groupby=["currency_id"],
                lazy=False,
            )
            credit = sum(
                map(
                    lambda x: ResCurrency.browse(x["currency_id"][0])._convert(
                        x["amount"],
                        user_currency_id,
                        self.env.user.company_id,
                        fields.Date.today(),
                    ),
                    credit_groups,
                )
            )

            debit_groups = AccountAnalyticLine.read_group(
                domain=domain + [("amount", "<", 0.0)],
                fields=["currency_id", "amount"],
                groupby=["currency_id"],
                lazy=False,
            )
            debit = sum(
                map(
                    lambda x: ResCurrency.browse(x["currency_id"][0])._convert(
                        x["amount"],
                        user_currency_id,
                        self.env.user.company_id,
                        fields.Date.today(),
                    ),
                    debit_groups,
                )
            )

            account.debit = abs(debit)
            account.credit = credit
            account.balance = account.credit - account.debit
        return res

    @api.constrains("parent_id")
    def check_recursion(self):
        for account in self:
            if not super(AccountAnalyticAccount, account)._check_recursion():
                raise UserError(_("You can not create recursive analytic accounts."))
        return True

    @api.onchange("parent_id")
    def _onchange_parent_id(self):
        for account in self:
            account.partner_id = account.parent_id.partner_id

    @api.depends("name", "parent_id.complete_name")
    def _compute_complete_name(self):
        for account in self:
            if account.parent_id:
                account.complete_name = _("%(parent)s / %(own)s") % {
                    "parent": account.parent_id.complete_name,
                    "own": account.name,
                }
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
                _("Please activate first parent account %s")
                % account.parent_id.complete_name
            )

    @api.depends("complete_name", "code", "partner_id.commercial_partner_id.name")
    def _compute_display_name(self):
        return super()._compute_display_name()

    def name_get(self):
        res = []
        for analytic in self:
            name = analytic.complete_name
            if analytic.code:
                name = ("[%(code)s] %(name)s") % {"code": analytic.code, "name": name}
            if analytic.partner_id:
                name = _("%(name)s - %(partner)s") % {
                    "name": name,
                    "partner": analytic.partner_id.commercial_partner_id.name,
                }
            res.append((analytic.id, name))
        return res

    def write(self, vals):
        if self and "active" in vals and not vals["active"]:
            self.mapped("child_ids").write({"active": False})
        return super().write(vals)
