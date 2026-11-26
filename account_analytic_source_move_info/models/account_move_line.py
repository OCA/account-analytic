# Copyright 2026 (APSL - Nagarro) Bernat Obrador
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import models
from odoo.tools.float_utils import float_round


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    def _prepare_analytic_distribution_line(
        self,
        distribution,
        account_ids,
        distribution_on_each_plan,
    ):
        vals = super()._prepare_analytic_distribution_line(
            distribution,
            account_ids,
            distribution_on_each_plan,
        )
        vals.update(
            self._prepare_source_move_analytic_info_vals(
                distribution=distribution,
                analytic_amount=vals.get("amount", 0.0),
            )
        )
        return vals

    def _prepare_source_move_analytic_info_vals(
        self,
        distribution,
        analytic_amount=0.0,
    ):
        self.ensure_one()

        move = self.move_id

        source_move_currency = (
            move.currency_id
            or self.currency_id
            or self.company_currency_id
            or self.company_id.currency_id
        )

        source_move_line_base_amount = (
            self._get_source_move_line_base_amount_for_analytic_info(analytic_amount)
        )
        source_move_base_amount = self._get_source_move_base_amount_for_analytic_info(
            analytic_amount
        )
        source_move_total_analytic_percentage = (
            self._get_source_move_total_analytic_percentage_for_analytic_info(
                distribution,
                source_move_line_base_amount,
                source_move_base_amount,
            )
        )

        return {
            "source_move_currency_id": source_move_currency.id,
            "analytic_percentage": distribution or 0.0,
            "source_move_line_base_amount": source_move_line_base_amount,
            "source_move_base_amount": source_move_base_amount,
            "source_move_total_analytic_percentage": (
                source_move_total_analytic_percentage
            ),
        }

    def _get_source_move_line_base_amount_for_analytic_info(
        self,
        analytic_amount=0.0,
    ):
        self.ensure_one()

        if self.move_id.is_invoice(include_receipts=True):
            amount = self._first_non_zero_amount_for_analytic_info(
                self.price_subtotal,
                self.amount_currency,
                self.balance,
            )
        else:
            amount = self._first_non_zero_amount_for_analytic_info(
                getattr(self, "price_total", 0.0),
                self.amount_currency,
                self.balance,
            )

        return self._signed_like_analytic_amount_for_analytic_info(
            amount,
            analytic_amount,
        )

    def _get_source_move_base_amount_for_analytic_info(
        self,
        analytic_amount=0.0,
    ):
        self.ensure_one()

        move = self.move_id

        if move.is_invoice(include_receipts=True):
            amount = move.amount_untaxed
        else:
            amount = self._first_non_zero_amount_for_analytic_info(
                move.amount_total,
                self.amount_currency,
                self.balance,
            )

        return self._signed_like_analytic_amount_for_analytic_info(
            amount,
            analytic_amount,
        )

    def _get_source_move_total_analytic_percentage_for_analytic_info(
        self,
        distribution,
        source_move_line_base_amount,
        source_move_base_amount,
    ):
        self.ensure_one()

        if not source_move_base_amount:
            return 0.0

        analytic_precision = self.env["decimal.precision"].precision_get(
            "Analytic Line"
        )

        percentage = (
            (distribution or 0.0)
            * source_move_line_base_amount
            / source_move_base_amount
        )

        return float_round(percentage, precision_digits=analytic_precision)

    def _first_non_zero_amount_for_analytic_info(self, *amounts):
        for amount in amounts:
            if amount:
                return amount
        return 0.0

    def _signed_like_analytic_amount_for_analytic_info(
        self,
        amount,
        analytic_amount,
    ):
        amount = amount or 0.0
        analytic_amount = analytic_amount or 0.0

        if not amount or not analytic_amount:
            return amount

        return abs(amount) if analytic_amount > 0.0 else -abs(amount)
