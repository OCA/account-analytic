# Copyright 2024 APSL-Nagarro - Miquel Alzanillas
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from odoo import models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    def _search_analytic_accounts_by_tag(self, analytic_tag_id):
        AccountAnalyticAccount = self.env["account.analytic.account"]
        account_analytic_acc_in_filter = (
            analytic_tag_id.spread_filter_analytic_account_ids
        )
        filter_operation = analytic_tag_id.spread_filter_operation

        if filter_operation and filter_operation == "exclude":
            return AccountAnalyticAccount.search(
                [
                    ("mapped_analytic_tag_ids", "in", [analytic_tag_id.id]),
                    ("id", "not in", account_analytic_acc_in_filter.ids),
                ]
            )

        if filter_operation and filter_operation == "include":
            return AccountAnalyticAccount.search(
                [
                    ("mapped_analytic_tag_ids", "in", [analytic_tag_id.id]),
                    ("id", "in", account_analytic_acc_in_filter.ids),
                ]
            )
        else:
            return AccountAnalyticAccount.search(
                [("mapped_analytic_tag_ids", "in", [analytic_tag_id.id])]
            )

    def _prepare_analytic_lines(self):
        """Check if any of the tags have spread option enabled"""
        vals = super()._prepare_analytic_lines()
        tag_ids_to_spread = self.analytic_tag_ids.filtered(lambda x: x.to_spread)
        if tag_ids_to_spread:
            for tag in tag_ids_to_spread:
                account_analytic_ids = self._search_analytic_accounts_by_tag(tag)
                number_of_aac = account_analytic_ids.__len__()
                if number_of_aac > 0:
                    line_amount = self.balance / number_of_aac
                    for aac in account_analytic_ids:
                        default_name = self.name or (
                            self.ref
                            or "/"
                            + " -- "
                            + (self.partner_id and self.partner_id.name or "/")
                        )
                        vals.append(
                            {
                                "name": default_name,
                                "date": self.date,
                                "account_id": aac.id,
                                "partner_id": self.partner_id.id,
                                "unit_amount": self.quantity,
                                "product_id": self.product_id
                                and self.product_id.id
                                or False,
                                "product_uom_id": self.product_uom_id
                                and self.product_uom_id.id
                                or False,
                                "amount": line_amount,
                                "general_account_id": self.account_id.id,
                                "tag_ids": [(6, 0, [tag.id])],
                                "ref": self.ref,
                                "move_line_id": self.id,
                                "user_id": self.move_id.invoice_user_id.id or self._uid,
                                "company_id": self.company_id.id or self.env.company.id,
                                "category": "invoice"
                                if self.move_id.is_sale_document()
                                else "vendor_bill"
                                if self.move_id.is_purchase_document()
                                else "other",
                            }
                        )
        return vals
