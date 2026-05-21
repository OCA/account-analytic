# Copyright 2022 Le Filament
# Copyright 2022 Moduon - Eduardo de Miguel
# Copyright 2024 (Nagarro - APSL) - Bernat Obrador
# Copyright 2025 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class AccountMoveUpdateAnalytic(models.TransientModel):
    _name = "account.move.update.analytic.wizard"
    _description = "Account Move Update Analytic Account Wizard"
    _inherit = "analytic.mixin"

    line_id = fields.Many2one("account.move.line", string="Invoice line")
    product_id = fields.Many2one(related="line_id.product_id")
    account_id = fields.Many2one(related="line_id.account_id")
    move_type = fields.Selection(selection="_move_type_selection", readonly=True)
    company_id = fields.Many2one(
        comodel_name="res.company", string="Company", readonly=True
    )
    current_analytic_distribution = fields.Json(
        related="line_id.analytic_distribution", string="Current Analytic Distribution"
    )

    def _move_type_selection(self):
        return self.env["account.move"].fields_get(allfields=["move_type"])[
            "move_type"
        ]["selection"]

    @api.model
    def default_get(self, fields):
        rec = super().default_get(fields)
        active_id = self.env.context.get("active_id", False)
        active_model = self.env.context.get("active_model", "account.move.line")
        if active_model == "account.move":
            moves = self.env["account.move"].browse(self.env.context.get("active_ids"))
            move_0 = moves[0]
            rec.update(
                {
                    "move_type": move_0.move_type,
                    "company_id": move_0.company_id.id,
                }
            )
        elif active_model == "account.move.line":
            aml = self.env["account.move.line"].browse(active_id)
            rec.update(
                {
                    "line_id": aml.id,
                    "product_id": aml.product_id.id,
                    "account_id": aml.account_id.id,
                    "move_type": aml.move_id.move_type,
                    "analytic_precision": aml.analytic_precision,
                    "company_id": aml.company_id.id,
                    "current_analytic_distribution": aml.analytic_distribution,
                    "analytic_distribution": aml.analytic_distribution,
                }
            )
        return rec

    def update_analytic_lines(self):
        self.ensure_one()
        # Validate if mandatory plans has 100%
        self.with_context(validate_analytic=True)._validate_distribution()
        if self.line_id:
            if (
                self.line_id.display_type == "product"
                and self.line_id.parent_state == "posted"
            ):
                # _sync_tax_lines skips posted moves (state != 'draft' guard in core),
                # so tax lines with 'Include in Analytic Cost' must be updated
                # explicitly.
                move = self.line_id.move_id
                analytic_taxes = self.line_id.tax_ids.filtered("analytic")
                extra_lines = self.env["account.move.line"]
                if analytic_taxes:
                    # Identify this product line's tax lines by combining two
                    # conditions: (1) the expected tax amount computed via
                    # compute_all, and (2) the current analytic distribution.
                    # Using both together handles same-amount/same-distribution
                    # edge cases that neither condition solves alone.
                    is_refund = move.move_type in ("out_refund", "in_refund")
                    price = self.line_id.price_unit * (1 - self.line_id.discount / 100)
                    taxes_res = analytic_taxes.compute_all(
                        price,
                        currency=move.currency_id,
                        quantity=self.line_id.quantity,
                        product=self.line_id.product_id,
                        partner=move.partner_id,
                        is_refund=is_refund,
                    )
                    expected = {
                        t["tax_repartition_line_id"]: abs(t["amount"])
                        for t in taxes_res["taxes"]
                        if t.get("tax_repartition_line_id")
                    }
                    current_dist = self.line_id.analytic_distribution
                    extra_lines = move.line_ids.filtered(
                        lambda line: line.display_type == "tax"
                        and line.tax_line_id in analytic_taxes
                        and line.analytic_distribution == current_dist
                        and move.currency_id.is_zero(
                            abs(line.balance)
                            - expected.get(line.tax_repartition_line_id.id, -1)
                        )
                    )
                    if not extra_lines:
                        # Fallback for merged tax lines: when multiple product
                        # lines share both the same tax and the same analytic
                        # distribution, Odoo combines them into one tax line
                        # whose balance is the sum — amount matching fails, so
                        # we check each candidate and split if needed.
                        merged_candidates = move.line_ids.filtered(
                            lambda line: line.display_type == "tax"
                            and line.tax_line_id in analytic_taxes
                            and line.analytic_distribution == current_dist
                        )
                        for merged_line in merged_candidates:
                            expected_amount = expected.get(
                                merged_line.tax_repartition_line_id.id, 0
                            )
                            can_split = (
                                expected_amount
                                and not move.currency_id.is_zero(
                                    abs(merged_line.balance) - expected_amount
                                )
                                and not merged_line.move_id.inalterable_hash
                            )
                            if can_split:
                                # Merged line: shrink to remaining amount,
                                # create a new line for this product's share.
                                sign = 1 if merged_line.balance >= 0 else -1
                                new_balance = sign * expected_amount
                                remaining_balance = merged_line.balance - new_balance
                                ctx = dict(self.env.context, check_move_validity=False)
                                merged_line.with_context(**ctx).write(
                                    {
                                        "debit": max(remaining_balance, 0),
                                        "credit": max(-remaining_balance, 0),
                                    }
                                )
                                self.env["account.move.line"].with_context(
                                    **ctx
                                ).create(
                                    {
                                        "move_id": move.id,
                                        "account_id": merged_line.account_id.id,
                                        "name": merged_line.name,
                                        "partner_id": merged_line.partner_id.id,
                                        "tax_line_id": merged_line.tax_line_id.id,
                                        "tax_repartition_line_id": (
                                            merged_line.tax_repartition_line_id.id
                                        ),
                                        "display_type": "tax",
                                        "debit": max(new_balance, 0),
                                        "credit": max(-new_balance, 0),
                                        "analytic_distribution": (
                                            self.analytic_distribution
                                        ),
                                    }
                                )
                            else:
                                extra_lines |= merged_line
                (
                    self.line_id | extra_lines
                ).analytic_distribution = self.analytic_distribution
            else:
                self.line_id.analytic_distribution = self.analytic_distribution
        else:
            moves = self.env["account.move"].browse(self.env.context.get("active_ids"))
            # _sync_tax_lines skips posted moves, so tax and payment_term lines
            # must be updated explicitly alongside invoice product lines.
            extra_lines = moves.line_ids.filtered(
                lambda line: line.display_type == "tax" and line.tax_line_id.analytic
            )
            (
                moves.invoice_line_ids | extra_lines
            ).analytic_distribution = self.analytic_distribution
