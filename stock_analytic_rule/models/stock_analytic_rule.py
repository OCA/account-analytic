# Copyright 2025 Bernat Obrador APSL-Nagarro
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class StockAnalyticRule(models.Model):
    _name = "stock.analytic.rule"
    _inherit = ["analytic.mixin"]
    _description = "Stock Analytic Rule"

    name = fields.Char()
    location_from_ids = fields.Many2many(
        "stock.location",
        "stock_analytic_model_location_from_rel",
        "model_id",
        "location_id",
        string="From",
    )

    location_dest_ids = fields.Many2many(
        "stock.location",
        "stock_analytic_model_location_dest_rel",
        "model_id",
        "location_id",
        string="To",
    )
    # Analytic Distribution for negative amounts
    # Positive one it's provided by the analytic mixin
    analytic_distribution_negative = fields.Json(
        "Negative Analytic Distribution",
        compute="_compute_analytic_distribution",
        store=True,
        copy=True,
        readonly=False,
    )

    amount_compute_type = fields.Selection(
        [
            ("category", _("Category")),
            ("product", _("Product")),
        ],
        string="Compute amount by",
        required=True,
        default="category",
        help="""
        Category: The amount is computed based on the product's
        category avg price, avg weight, and supplement.
        Product: The amount is computed based on the product's price.
        """,
    )

    include_taxes = fields.Boolean(
        default=False,
        help="If checked, the amount will include taxes when computed by product.",
    )

    financial_account_id = fields.Many2one(
        "account.account",
        string="Financial Account",
        domain=[("deprecated", "=", False)],
        help="Financial account to use for the analytic lines.",
    )

    active = fields.Boolean(default=True)
    company_id = fields.Many2one(
        "res.company",
        default=lambda self: self.env.company,
        required=True,
    )

    def copy(self, default=None):
        default = dict(default or {})
        default["name"] = f"{self.name} (copy)"
        self = self.with_context(bypass_combination_check=True)
        return super().copy(default)

    def write(self, vals):
        res = super().write(vals)
        self._check_unique_combination()
        return res

    @api.constrains("location_from_ids", "location_dest_ids")
    def _check_unique_combination(self):
        """
        This method ensures that the combination of 'From', 'To',
        is unique.
        """
        if self.env.context.get("bypass_combination_check"):
            # Avoid validation when record is being copied
            return
        for record in self:
            others = self.search([("id", "!=", record.id)])
            for other in others:
                if set(other.location_from_ids.ids) == set(
                    record.location_from_ids.ids
                ) and set(other.location_dest_ids.ids) == set(
                    record.location_dest_ids.ids
                ):
                    raise ValidationError(
                        _(
                            """A Stock Analytic Rule with the same
                            'From' and 'To' already exists."""
                        )
                    )

    def action_open_form(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Stock Analytic Rule",
            "view_mode": "form",
            "res_model": "stock.analytic.rule",
            "res_id": self.id,
            "target": "current",
        }

    def _get_amount_by_product(self, product, quantity, partner=None):
        """
        Computes the amount for the analytic line based on the product's price + taxes.
        This method is used when the amount_compute_type is set to 'product'.
        """
        if not self.include_taxes:
            return product.lst_price * quantity

        taxes = product.taxes_id.filtered(lambda t: t.company_id == self.env.company)
        price_unit = product.lst_price
        tax_result = taxes.compute_all(
            price_unit, quantity=quantity, product=product, partner=partner
        )
        return tax_result["total_included"]

    def _get_amount_by_category(self, product, quantity):
        """
        Computes the amount for the analytic line based on the product's category.
        This method is used when the amount_compute_type is set to 'category'.
        """
        category = product.categ_id
        self._validation_checks(category)
        return (category.avg_price * (category.avg_weight * quantity)) + (
            (category.avg_weight * quantity) * category.supplement
        )

    def _compute_amount(self, product, quantity, partner=None):
        """
        Computes the amount for the analytic line.
        """
        if self.amount_compute_type == "product":
            return self._get_amount_by_product(product, quantity, partner)

        return self._get_amount_by_category(product, quantity)

    def _prepare_analytic_line(
        self, amount, stock_move_id, financial_account_id, company_id
    ):
        """Creates dict for a single analytic line."""
        return {
            "name": self.name or "",
            "amount": amount,
            "stock_move_id": stock_move_id,
            "general_account_id": financial_account_id.id,
            "company_id": company_id,
        }

    def _create_analytic_lines(
        self, amount, product, stock_move_id, company_id, is_reversal=False
    ):
        """Generates analytic lines for both positive and negative accounts.
        is_reversal is neeeded to know if the lines comes from a devolution
        wich means we need to change the sign of the amount.
        """
        analytic_lines_to_create = []
        # Change the sign of the amount if it's the reversal rule.
        positive_amount = amount if not is_reversal else -amount
        negative_amount = -amount if not is_reversal else amount

        if self.analytic_distribution:
            analytic_lines_to_create.extend(
                self._split_amount_by_analytic_distribution(
                    positive_amount,
                    self.analytic_distribution,
                    stock_move_id,
                    company_id,
                    self.financial_account_id,
                )
            )

        if self.analytic_distribution_negative:
            analytic_lines_to_create.extend(
                self._split_amount_by_analytic_distribution(
                    negative_amount,
                    self.analytic_distribution_negative,
                    stock_move_id,
                    company_id,
                    self.financial_account_id,
                )
            )

        self.env["account.analytic.line"].create(analytic_lines_to_create)

    def _split_amount_by_analytic_distribution(
        self,
        amount,
        analytic_distribution,
        stock_move_id,
        company_id,
        financial_account_id=None,
    ):
        """Allocates the amount based on the analytic distribution."""
        analytic_lines = []
        for account_id, percentage in analytic_distribution.items():
            ids = [int(x) for x in account_id.split(",")]
            analytic_accounts = self.env["account.analytic.account"].browse(ids)
            calculated_amount = amount * (percentage / 100)
            line_to_add = self._prepare_analytic_line(
                calculated_amount, stock_move_id, financial_account_id, company_id
            )

            for account in analytic_accounts:
                plan_field_name = account.root_plan_id._column_name()

                if plan_field_name:
                    line_to_add[plan_field_name] = account.id
            analytic_lines.append(line_to_add)
        return analytic_lines

    def _validation_checks(self, category):
        if not category.avg_weight > 0:
            raise ValidationError(
                _(
                    """This move has to generate analytic
                    lines so the category must have a weight greater than 0.\n
                    Please, check the category %s weight."""
                )
                % category.name
            )

        if not category.avg_price > 0:
            raise ValidationError(
                _(
                    """This move has to generate analytic lines
                    so the category must have a price greater than 0.\n
                    Please, check the category %s price."""
                )
                % category.name
            )

    @api.model
    def generate_analytic_lines(self, stock_move):
        """Generates analytic lines based on matching stock analytic rules."""

        product = stock_move.product_id
        quantity = stock_move.quantity
        location_from_id = stock_move.location_id.id
        location_dest_id = stock_move.location_dest_id.id
        company_id = stock_move.company_id.id
        partner = stock_move.partner_id

        record = self.search(
            [
                ("location_from_ids", "in", [location_from_id]),
                ("location_dest_ids", "in", [location_dest_id]),
                ("active", "=", True),
                ("company_id", "=", company_id),
            ],
            limit=1,
        )

        if record:
            # If the stock moves matches with the rule criteria,
            # then generate the analytic lines.
            amount = record._compute_amount(product, quantity, partner=partner)
            record._create_analytic_lines(amount, product, stock_move.id, company_id)
            return
        else:
            # Look for the reversal rule, if it exists.
            reversal = self.search(
                [
                    ("location_from_ids", "in", [location_dest_id]),
                    ("location_dest_ids", "in", [location_from_id]),
                    ("active", "=", True),
                    ("company_id", "=", company_id),
                ],
                limit=1,
            )

            if reversal:
                amount = reversal._compute_amount(product, quantity, partner=partner)
                reversal._create_analytic_lines(
                    amount, product, stock_move.id, company_id, is_reversal=True
                )
