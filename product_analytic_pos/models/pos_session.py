from collections import defaultdict

from odoo import models
from odoo.tools import frozendict


class PosSession(models.Model):
    _inherit = "pos.session"

    def _get_sale_grouping_key(self, base_line):
        return (
            base_line["account_id"].id,
            -1 if base_line["is_refund"] else 1,
            tuple(
                base_line["record"]
                .tax_ids_after_fiscal_position.flatten_taxes_hierarchy()
                .ids
            ),
            tuple(base_line["tax_tag_ids"].ids),
            base_line["product_id"].id
            if self.config_id.is_closing_entry_by_product
            else False,
            frozendict(base_line.get("analytic_distribution") or {}),
        )

    def _get_split_sales(self):
        AccountTax = self.env["account.tax"]

        def amounts():
            return {"amount": 0.0, "amount_converted": 0.0}

        sales = defaultdict(amounts)
        for order in self._get_closed_orders().filtered(
            lambda order: not order.is_invoiced
        ):
            base_lines = order.with_context(
                linked_to_pos=True
            )._prepare_tax_base_line_values()
            AccountTax._add_tax_details_in_base_lines(base_lines, order.company_id)
            AccountTax._round_base_lines_tax_details(base_lines, order.company_id)
            AccountTax._add_accounting_data_in_base_lines_tax_details(
                base_lines, order.company_id, include_caba_tags=True
            )
            tax_results = AccountTax._prepare_tax_lines(base_lines, order.company_id)
            for base_line, to_update in tax_results["base_lines_to_update"]:
                sale_key = self._get_sale_grouping_key(base_line)
                sales[sale_key] = self._update_amounts(
                    sales[sale_key],
                    {
                        "amount": to_update["amount_currency"],
                        "amount_converted": to_update["balance"],
                    },
                    order.date_order,
                )
                if self.config_id.is_closing_entry_by_product:
                    sales[sale_key] = self._update_quantities(
                        sales[sale_key], base_line["quantity"]
                    )
        return sales

    def _accumulate_amounts(self, data):
        data = super()._accumulate_amounts(data)
        data["sales"] = self._get_split_sales()
        return data

    def _get_sale_vals(self, key, sale_vals):
        analytic_distribution = False
        if len(key) == 6:
            *base_key, analytic_distribution = key
            key = tuple(base_key)
        vals = super()._get_sale_vals(key, sale_vals)
        if analytic_distribution:
            vals["analytic_distribution"] = dict(analytic_distribution)
        return vals
