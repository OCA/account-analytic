# Copyright 2026 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import json
from datetime import datetime, time

from odoo import Command, _, api, fields, models
from odoo.exceptions import UserError


class MrpWipAccountingLine(models.TransientModel):
    _name = "mrp.account.wip.accounting.line"
    _inherit = ["mrp.account.wip.accounting.line", "analytic.mixin"]

    # Required by analytic.mixin for validating analytic distribution against
    # company-specific analytic plans (see analytic.mixin._validate_distribution)
    company_id = fields.Many2one(
        "res.company",
        related="wip_accounting_id.journal_id.company_id",
        store=True,
        readonly=True,
    )


class MrpWipAccounting(models.TransientModel):
    _inherit = "mrp.account.wip.accounting"

    @api.depends("date")
    def _compute_line_ids(self):
        wip_account_id = self.env.company.account_production_wip_account_id.id
        for wizard in self:
            if not wizard.mo_ids:
                continue
            # Group MOs by analytic distribution pattern
            mo_groups = {}
            for mo in wizard.mo_ids:
                key = (
                    json.dumps(mo.analytic_distribution, sort_keys=True)
                    if mo.analytic_distribution
                    else ""
                )
                mo_groups.setdefault(key, self.env["mrp.production"])
                mo_groups[key] |= mo
            # Create lines per group with analytic on WIP lines
            cut_date = datetime.combine(wizard.date, time.max)
            all_commands = [Command.clear()]
            for key, mos in mo_groups.items():
                line_cmds = wizard._get_line_vals(mos, cut_date)
                dist = mos[0].analytic_distribution if key else False
                for _op, _id, vals in line_cmds:
                    if dist and vals.get("account_id") == wip_account_id:
                        vals["analytic_distribution"] = dist
                all_commands.extend(line_cmds)
            wizard.line_ids = all_commands
        # Fall back to super for wizards without MOs
        unhandled = self.filtered(lambda w: not w.line_ids)
        if unhandled:
            super(MrpWipAccounting, unhandled)._compute_line_ids()
        return

    # TODO: Propose a refactor to the original method to minimize the change
    def confirm(self):
        """Override to include analytic_distribution in WIP move lines."""
        if not any(mo.analytic_distribution for mo in self.mo_ids):
            return super().confirm()
        self.ensure_one()
        if (
            self.env.company.currency_id.compare_amounts(
                sum(self.line_ids.mapped("credit")), sum(self.line_ids.mapped("debit"))
            )
            != 0
        ):
            raise UserError(
                _(
                    "Please make sure the total credit amount equals "
                    "the total debit amount."
                )
            )
        if self.reversal_date <= self.date:
            raise UserError(_("Reversal date must be after the posting date."))
        move_line_vals = []
        for line in self.line_ids:
            vals = {
                "name": line.label,
                "account_id": line.account_id.id,
                "debit": line.debit,
                "credit": line.credit,
                "analytic_distribution": line.analytic_distribution,
            }
            move_line_vals.append(Command.create(vals))
        move = (
            self.env["account.move"]
            .sudo()
            .create(
                {
                    "journal_id": self.journal_id.id,
                    "wip_production_ids": self.mo_ids.ids,
                    "date": self.date,
                    "ref": self.reference,
                    "move_type": "entry",
                    "line_ids": move_line_vals,
                }
            )
        )
        move._post()
        move._reverse_moves(
            default_values_list=[
                {
                    "ref": _("Reversal of: %s", self.reference),
                    "wip_production_ids": self.mo_ids.ids,
                    "date": self.reversal_date,
                }
            ]
        )._post()
