# Copyright 2023 ForgeFlow S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import models


class AccountMove(models.Model):

    _inherit = "account.move"

    def get_payment_term_candidate_vals(
        self, balance, amount_currency, date_maturity, account
    ):
        # Compute accounting fields.
        candidate = {
            "name": self.payment_reference or "",
            "debit": balance < 0.0 and -balance or 0.0,
            "credit": balance > 0.0 and balance or 0.0,
            "quantity": 1.0,
            "amount_currency": -amount_currency,
            "date_maturity": date_maturity,
            "move_id": self.id,
            "currency_id": self.currency_id.id,
            "account_id": account.id,
            "partner_id": self.commercial_partner_id.id,
            "exclude_from_invoice_tab": True,
        }
        return candidate

    def get_candidate_vals_update(self, date_maturity, amount_currency, balance):
        return {
            "date_maturity": date_maturity,
            "amount_currency": -amount_currency,
            "debit": balance < 0.0 and -balance or 0.0,
            "credit": balance > 0.0 and balance or 0.0,
        }

    def post_process_term_lines(
        self,
        _get_payment_terms_computation_date,
        _get_payment_terms_account,
        _compute_payment_terms,
        _compute_diff_payment_terms_lines,
    ):
        existing_terms_lines = self.line_ids.filtered(
            lambda line: line.account_id.user_type_id.type in ("receivable", "payable")
        )
        others_lines = self.line_ids.filtered(
            lambda line: line.account_id.user_type_id.type
            not in ("receivable", "payable")
        )
        company_currency_id = (self.company_id or self.env.company).currency_id
        total_balance = sum(
            others_lines.mapped(lambda l: company_currency_id.round(l.balance))
        )
        total_amount_currency = sum(others_lines.mapped("amount_currency"))

        if not others_lines:
            self.line_ids -= existing_terms_lines
            return

        computation_date = _get_payment_terms_computation_date(self)
        account = _get_payment_terms_account(self, existing_terms_lines)
        to_compute = _compute_payment_terms(
            self, computation_date, total_balance, total_amount_currency
        )
        new_terms_lines = _compute_diff_payment_terms_lines(
            self, existing_terms_lines, account, to_compute
        )

        # Remove old terms lines that are no longer needed.
        self.line_ids -= existing_terms_lines - new_terms_lines

        if new_terms_lines:
            self.payment_reference = new_terms_lines[-1].name or ""
            self.invoice_date_due = new_terms_lines[-1].date_maturity
