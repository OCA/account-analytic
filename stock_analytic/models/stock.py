# Copyright 2013 Julius Network Solutions
# Copyright 2015 Clear Corp
# Copyright 2016 OpenSynergy Indonesia
# Copyright 2017 ForgeFlow S.L.
# Copyright 2018 Hibou Corp.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class StockMove(models.Model):
    _inherit = "stock.move"

    analytic_account_id = fields.Many2one(
        string="Analytic Account",
        comodel_name="account.analytic.account",
    )
    analytic_tag_ids = fields.Many2many("account.analytic.tag", string="Analytic Tags")

    def _generate_valuation_lines_data(
        self,
        partner_id,
        qty,
        debit_value,
        credit_value,
        debit_account_id,
        credit_account_id,
        description,
    ):
        res = super()._generate_valuation_lines_data(
            partner_id,
            qty,
            debit_value,
            credit_value,
            debit_account_id,
            credit_account_id,
            description,
        )
        for key, value in res.items():
            # config stock account line debit, accounting all line (exclude price diff)
            if (
                self.company_id.stock_account_line_debit
                and key != "price_diff_line_vals"
            ):
                value["analytic_account_id"] = self.analytic_account_id.id
                value["analytic_tag_ids"] = [(6, 0, self.analytic_tag_ids.ids)]
                continue
            if (
                value["account_id"]
                != self.product_id.categ_id.property_stock_valuation_account_id.id
            ):
                value["analytic_account_id"] = self.analytic_account_id.id
                value["analytic_tag_ids"] = [(6, 0, self.analytic_tag_ids.ids)]
        return res

    def _prepare_procurement_values(self):
        """
        Allows to transmit analytic account from moves to new
        moves through procurement.
        """
        res = super()._prepare_procurement_values()
        if self.analytic_account_id:
            res.update(
                {
                    "analytic_account_id": self.analytic_account_id.id,
                }
            )
        if self.analytic_tag_ids:
            res.update({"analytic_tag_ids": [(6, 0, self.analytic_tag_ids.ids)]})
        return res

    @api.model
    def _prepare_merge_moves_distinct_fields(self):
        fields = super()._prepare_merge_moves_distinct_fields()
        fields.append("analytic_account_id")
        return fields

    def _prepare_move_line_vals(self, quantity=None, reserved_quant=None):
        """
        We fill in the analytic account when creating the move line from
        the move
        """
        res = super()._prepare_move_line_vals(
            quantity=quantity, reserved_quant=reserved_quant
        )
        if self.analytic_account_id:
            res.update({"analytic_account_id": self.analytic_account_id.id})
        if self.analytic_tag_ids:
            res.update({"analytic_tag_ids": [(6, 0, self.analytic_tag_ids.ids)]})
        return res


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    analytic_account_id = fields.Many2one(comodel_name="account.analytic.account")
    analytic_tag_ids = fields.Many2many(
        comodel_name="account.analytic.tag",
        string="Analytic Tags",
    )

    @api.model
    def _prepare_stock_move_vals(self):
        """
        In the case move lines are created manually, we should fill in the
        new move created here with the analytic account if filled in.
        """
        res = super()._prepare_stock_move_vals()
        if self.analytic_account_id:
            res.update({"analytic_account_id": self.analytic_account_id.id})
        if self.analytic_tag_ids:
            res.update({"analytic_tag_ids": [(6, 0, self.analytic_tag_ids.ids)]})
        return res
