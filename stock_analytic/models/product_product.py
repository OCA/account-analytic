# Copyright (C) 2020 Brahoo
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class ProductProduct(models.Model):
    _inherit = "product.product"

    @api.model
    def _anglo_saxon_sale_move_lines(
        self,
        name,
        product,
        uom,
        qty,
        price_unit,
        currency=False,
        amount_currency=False,
        fiscal_position=False,
        account_analytic=False,
        analytic_tags=False,
    ):
        res = super()._anglo_saxon_sale_move_lines(
            name,
            product,
            uom,
            qty,
            price_unit,
            currency=currency,
            amount_currency=amount_currency,
            fiscal_position=fiscal_position,
            account_analytic=account_analytic,
            analytic_tags=analytic_tags,
        )
        if res:
            res[0]["account_analytic_id"] = account_analytic and account_analytic.id
            res[0]["analytic_tag_ids"] = (
                analytic_tags
                and analytic_tags.ids
                and [(6, 0, analytic_tags.ids)]
                or False
            )
        return res
