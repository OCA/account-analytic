# Copyright 2026 Innovyou
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class AccountAnalyticLine(models.Model):
    _inherit = "account.analytic.line"

    profit_cost_category = fields.Selection(
        selection=[
            ("customer_invoice", "Customer Invoice"),
            ("vendor_bill", "Vendor Bill"),
            ("timesheet", "Timesheet"),
            ("costs_distribution", "Costs Distribution"),
            ("manual", "Manual"),
            ("other", "Other"),
        ],
        string="Profit/Cost Category",
        compute="_compute_profit_cost_category",
        store=True,
        readonly=False,
    )
    indirect_cost_distribution_operation_id = fields.Many2one(
        "indirect.cost.distribution.operation",
        string="Cost Distribution Operation",
        ondelete="cascade",
        index=True,
        help="The cost distribution operation that created this line.",
    )
    indirect_cost_distribution_model_id = fields.Many2one(
        "indirect.cost.distribution.model",
        string="Cost Distribution Model",
        index=True,
        help="The distribution model used for this distributed cost.",
    )
    distributed_by_operation_id = fields.Many2one(
        "indirect.cost.distribution.operation",
        string="Distributed By Operation",
        index=True,
        help="The operation that distributed this indirect cost line "
        "to profit centres.",
    )

    @api.depends(
        "move_line_id.move_id.move_type",
        "project_id",
        "indirect_cost_distribution_operation_id",
    )
    def _compute_profit_cost_category(self):
        for line in self:
            if line.move_line_id and line.move_line_id.move_id.is_sale_document():
                line.profit_cost_category = "customer_invoice"
            elif line.move_line_id and line.move_line_id.move_id.is_purchase_document():
                line.profit_cost_category = "vendor_bill"
            elif line.project_id:
                line.profit_cost_category = "timesheet"
            elif line.indirect_cost_distribution_operation_id:
                line.profit_cost_category = "costs_distribution"
            else:
                line.profit_cost_category = "other"
