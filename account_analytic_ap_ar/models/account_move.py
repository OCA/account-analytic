# Copyright 2021 Tecnativa Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


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
        all_lines_are_analytic = False
        if self:
            all_analytic_ids = self.invoice_line_ids.mapped("analytic_account_id").ids
            if not all_analytic_ids:
                return super().post_process_term_lines(
                    _get_payment_terms_computation_date,
                    _get_payment_terms_account,
                    _compute_payment_terms,
                    _compute_diff_payment_terms_lines,
                )
            else:
                all_analytic_accounts = [
                    analytic_model.browse(aid) for aid in all_analytic_ids
                ]
                if len(
                    self.invoice_line_ids.filtered(
                        lambda l: l.analytic_account_id == analytic_model
                    )
                ):
                    all_analytic_accounts.insert(0, analytic_model)
                else:
                    all_lines_are_analytic = True
        else:
            return super().post_process_term_lines(
                _get_payment_terms_computation_date,
                _get_payment_terms_account,
                _compute_payment_terms,
                _compute_diff_payment_terms_lines,
            )
        tax_lines_taken = False
        for aa in all_analytic_accounts:
            existing_terms_lines = self.line_ids.filtered(
                lambda line: line.account_id.user_type_id.type
                in ("receivable", "payable")
                and (
                    line.analytic_account_id == aa
                    or line.analytic_account_id not in all_analytic_accounts
                )
            )
            if not all_lines_are_analytic:
                # filtered is corner case for removed analytic accounts
                others_lines = self.line_ids.filtered(
                    lambda line: line.account_id.user_type_id.type
                    not in ("receivable", "payable")
                    and line.analytic_account_id == aa
                ).filtered(lambda l: l.analytic_account_id in all_analytic_accounts)
            else:
                others_lines = self.line_ids.filtered(
                    lambda line: line.account_id.user_type_id.type
                    not in ("receivable", "payable")
                    and line.analytic_account_id == aa
                ).filtered(lambda l: l.analytic_account_id in all_analytic_accounts)
                # If all lines are analytic only tax is no analytic
                # we assign the tax to one of the lines for simplicity
                tax_lines = self.line_ids.filtered(
                    lambda line: line.account_id.user_type_id.type
                    not in ("receivable", "payable")
                    and line.analytic_account_id == analytic_model
                )
                if not tax_lines_taken:
                    others_lines += tax_lines
                    tax_lines_taken = True
            company_currency_id = (self.company_id or self.env.company).currency_id
            total_balance = sum(
                others_lines.mapped(lambda l: company_currency_id.round(l.balance))
            )
            total_amount_currency = sum(others_lines.mapped("amount_currency"))

            if not others_lines:
                self.line_ids -= existing_terms_lines
                existing_terms_lines = self.line_ids.filtered(
                    lambda line: line.account_id.user_type_id.type
                    in ("receivable", "payable")
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
                continue

            computation_date = _get_payment_terms_computation_date(self)
            account = _get_payment_terms_account(self, existing_terms_lines)
            to_compute = _compute_payment_terms(
                self, computation_date, total_balance, total_amount_currency
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
