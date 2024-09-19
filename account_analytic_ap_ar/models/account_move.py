# Copyright 2024 ForgeFlow S.L.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import models


class AccountMove(models.Model):
    _inherit = "account.move"

    def get_candidate_vals_update(self, date_maturity, amount_currency, balance):
        res = super().get_candidate_vals_update(date_maturity, amount_currency, balance)
        analytic_account = self.env.context.get("analytic_account", False)
        if analytic_account:
            res.update(analytic_account_id=analytic_account.id)
        else:
            res.update(analytic_account_id=False)
        return res

    def get_payment_term_candidate_vals(
        self, balance, amount_currency, date_maturity, account
    ):
        candidate = super().get_payment_term_candidate_vals(
            balance, amount_currency, date_maturity, account
        )
        analytic_account = self.env.context.get("analytic_account", False)
        if analytic_account:
            candidate.update(analytic_account_id=analytic_account.id)
        else:
            candidate.update(analytic_account_id=False)
        return candidate

    def post_process_term_lines(
        self,
        _get_payment_terms_computation_date,
        _get_payment_terms_account,
        _compute_payment_terms,
        _compute_diff_payment_terms_lines,
    ):
        analytic_model = self.env["account.analytic.account"]
        new_terms_lines = False
        if self:
            any_analytic_ids = self.invoice_line_ids.mapped("analytic_account_id").ids
            if not any_analytic_ids:
                return super().post_process_term_lines(
                    _get_payment_terms_computation_date,
                    _get_payment_terms_account,
                    _compute_payment_terms,
                    _compute_diff_payment_terms_lines,
                )
            else:
                all_analytic_accounts = [
                    analytic_model.browse(aid) for aid in any_analytic_ids
                ]
                if len(
                    self.invoice_line_ids.filtered(
                        lambda l: l.analytic_account_id == analytic_model
                    )
                ):
                    all_analytic_accounts.insert(0, analytic_model)
                else:
                    pass
        else:
            return super().post_process_term_lines(
                _get_payment_terms_computation_date,
                _get_payment_terms_account,
                _compute_payment_terms,
                _compute_diff_payment_terms_lines,
            )
        for aa in all_analytic_accounts:
            existing_terms_lines = self.line_ids.filtered(
                lambda line: line.account_id.user_type_id.type
                in ("receivable", "payable")
                and (
                    line.analytic_account_id == aa
                    # this or is to prevent error when manually editing and removing the AA
                    or line.analytic_account_id not in all_analytic_accounts
                )
            )
            invoice_lines = self.invoice_line_ids.filtered(
                lambda line: line.analytic_account_id == aa
            )
            invoices_balance = sum(invoice_lines.mapped("balance"))
            aa_total_balance = invoices_balance
            total_amount_currency = invoices_balance
            taxes = invoice_lines.mapped("tax_ids")
            for tax in taxes:
                (
                    tax_balance,
                    tax_amount_currency,
                ) = self._get_tax_balance_by_analytic_account_and_tax(aa, tax)
                invoice_lines_with_same_tax = self.line_ids.filtered(
                    lambda line: tax._origin.id in line.tax_ids.ids
                )  # this works for newId and saved ones
                total_invoice_balance_for_same_tax = sum(
                    invoice_lines_with_same_tax.mapped("balance")
                )
                try:
                    percentage = invoices_balance / total_invoice_balance_for_same_tax
                except ZeroDivisionError:
                    percentage = 1
                aa_total_balance += tax_balance * percentage
                total_amount_currency += tax_amount_currency * percentage

            computation_date = _get_payment_terms_computation_date(self)
            account = _get_payment_terms_account(self, existing_terms_lines)
            to_compute = _compute_payment_terms(
                self, computation_date, aa_total_balance, total_amount_currency
            )

            if new_terms_lines:
                new_terms_lines += _compute_diff_payment_terms_lines(
                    self.with_context(analytic_account=aa),
                    existing_terms_lines,
                    account,
                    to_compute,
                )
            else:
                new_terms_lines = _compute_diff_payment_terms_lines(
                    self.with_context(analytic_account=aa),
                    existing_terms_lines,
                    account,
                    to_compute,
                )

            # Remove old terms lines that are no longer needed.
            self.line_ids -= existing_terms_lines - new_terms_lines

        if new_terms_lines:
            self.payment_reference = new_terms_lines[-1].name or ""
            self.invoice_date_due = new_terms_lines[-1].date_maturity
        return True

    def _get_tax_balance_by_analytic_account_and_tax(self, aa, tax):
        tax_lines = self.line_ids.filtered("tax_line_id").filtered(
            lambda l: l.tax_line_id.id in tax.ids
        )
        tax_balance = sum(tax_lines.mapped("balance"))
        tax_amount_currency = sum(tax_lines.mapped("amount_currency"))
        return tax_balance, tax_amount_currency
