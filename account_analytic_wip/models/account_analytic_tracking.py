# Copyright (C) 2021 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import api, fields, models
from odoo.tools import float_is_zero


class AnalyticTrackingItem(models.Model):
    """
    Tracking Items provide a central point to report WIP and Variances.
    Expected amounts are stored on a key event, such a confirming an order.
    Done amounts are captured by Analytic items.
    They can then be posted as journal entries.
    """

    _name = "account.analytic.tracking.item"
    _description = "Cost Tracking Item"

    name = fields.Char(compute="_compute_name", store=True)
    date = fields.Date(default=fields.Date.today())
    analytic_id = fields.Many2one(
        "account.analytic.account",
        string="Analytic Account",
        required=True,
        ondelete="restrict",
    )
    product_id = fields.Many2one(
        "product.product", string="Cost Product", ondelete="restrict"
    )
    activity_cost_id = fields.Many2one("activity.cost.rule", "Activity Cost Rule")

    # Related calculated data
    company_id = fields.Many2one(
        "res.company", related="analytic_id.company_id", store=True
    )
    product_categ_id = fields.Many2one(
        "product.category", related="product_id.categ_id", store=True
    )
    # Analytic Items, to compute WIP actuals from
    analytic_line_ids = fields.One2many(
        "account.analytic.line",
        "analytic_tracking_item_id",
        string="Analytic Items",
        help="Related analytic items with the project actuals.",
    )
    # Journal Entries, to compute Posted actuals from
    account_move_ids = fields.One2many(
        "account.move",
        "analytic_tracking_item_id",
        string="Journal Entries",
        help="Related journal entries with the posted WIP.",
    )
    state = fields.Selection(
        [
            ("open", "Open"),  # In progress
            ("done", "Done"),  # Completed but not Posted
            ("close", "Locked"),  # Completed and Posted
            ("cancel", "Cancelled"),
        ],
        default="open",
        help="Open operations are in progress, no negative variances are computed. "
        "Done operations are completed, negative variances are computed. "
        "Locked operations are done and posted, no more actions to do.",
    )
    to_calculate = fields.Boolean(compute="_compute_to_calculate")

    parent_id = fields.Many2one(
        "account.analytic.tracking.item", "Parent Tracking Item", ondelete="cascade"
    )
    child_ids = fields.One2many(
        "account.analytic.tracking.item", "parent_id", string="Child Tracking Items"
    )

    # Planned Amount
    planned_qty = fields.Float()
    planned_amount = fields.Float()

    # Actual Amounts
    actual_amount = fields.Float(
        compute="_compute_actual_amounts",
        store=True,
        help="Total cost amount of the related Analytic Items. "
        "These Analytic Items are generated when a cost is incurred, "
        "and will later generated WIP and Variance Journal Entries.",
    )
    wip_actual_amount = fields.Float(
        compute="_compute_actual_amounts",
        store=True,
        help="Actual amount incurred below the planned amount limit.",
    )
    variance_actual_amount = fields.Float(
        compute="_compute_actual_amounts",
        store=True,
        help="Actual amount incurred above the planned amount limit.",
    )
    remaining_actual_amount = fields.Float(
        compute="_compute_actual_amounts",
        store=True,
        help="Actual amount planned and not yet consumed.",
    )
    pending_amount = fields.Float(
        compute="_compute_actual_amounts",
        store=True,
        help="Amount not yet posted to journal entries.",
    )

    # Accounted Amounts
    accounted_amount = fields.Float(
        help="Amount accounted in Journal Entries. "
        "Directly set by the routine creating the Journal Entries, "
        "and not directly read from the jpunral items."
    )
    wip_accounted_amount = fields.Float(
        help="Accounted amount incurred below the planned amount limit."
    )
    variance_accounted_amount = fields.Float(
        help="Accounted amount incurred above the planned amount limit."
    )

    @api.depends("product_id")
    def _compute_name(self):
        for item in self:
            item.name = item.product_id.display_name

    @api.depends("state", "child_ids")
    def _compute_to_calculate(self):
        for item in self:
            item.to_calculate = (
                item.state != "cancel" and not item.child_ids and item.product_id
            )

    @api.depends(
        "analytic_line_ids.amount",
        "parent_id.analytic_line_ids.amount",
        "planned_amount",
        "accounted_amount",
        "state",
        "child_ids",
    )
    def _compute_actual_amounts(self):
        for item in self:
            if not item.to_calculate or item.child_ids:
                item.actual_amount = 0
            else:
                all_actuals = item.analytic_line_ids or item.parent_id.analytic_line_ids
                all_actuals |= all_actuals.child_ids
                product_actuals = all_actuals.filtered(
                    lambda x: x.product_id == item.product_id
                )
                item.actual_amount = (
                    -sum(product_actuals.mapped("amount_abcost")) or 0.0
                )

            item.pending_amount = item.actual_amount - item.accounted_amount
            if item.planned_amount:
                item.wip_actual_amount = min(item.actual_amount, item.planned_amount)
            else:
                item.wip_actual_amount = item.actual_amount

            if not item.to_calculate or not item.planned_amount:
                item.remaining_actual_amount = 0
                item.variance_actual_amount = 0
            elif item.state == "open":
                # Negative variances show in the Remaining column
                item.remaining_actual_amount = (
                    item.planned_amount - item.wip_actual_amount
                )
                item.variance_actual_amount = max(
                    item.actual_amount - item.planned_amount, 0
                )
            else:
                # Negative variances show in the Variance column
                item.remaining_actual_amount = 0
                item.variance_actual_amount = item.actual_amount - item.planned_amount

    def _prepare_account_move_head(self, journal):
        return {
            "journal_id": journal.id,
            "date": self.env.context.get(
                "force_period_date", fields.Date.context_today(self)
            ),
            "ref": self.display_name,
            "move_type": "entry",
            "analytic_tracking_item_id": self.id,
        }

    def _prepare_account_move_line(self, account, amount, account_role=None):
        # Note: do not set analytic_Account_id,
        # as that triggers a (repeated) Analytic Item
        return {
            "name": self.display_name,
            "product_id": self.product_id.id,
            "product_uom_id": self.product_id.uom_id.id,
            "ref": self.display_name,
            "account_id": account.id,
            "debit": amount if amount > 0.0 else 0.0,
            "credit": -amount if amount < 0.0 else 0.0,
            "is_wip_line": account_role == "stock_wip",
        }

    def _get_accounting_data_for_valuation(self):
        """
        Extension hook to set the accounts to use
        """
        accounts = self.product_id.product_tmpl_id.get_product_accounts()
        categ = self.with_company(self.company_id).product_id.categ_id
        accounts.update(
            {
                "wip_journal": categ.property_wip_journal_id,
                "stock_wip": categ.property_wip_account_id,
                "stock_variance": categ.property_variance_account_id,
            }
        )
        return accounts

    def _get_journal_entries_wip(self, wip_amount=0.0, variance_amount=0.0):
        """
        Extension hook to set the journal items for WIP records
        """
        return {
            "stock_valuation": -(wip_amount + variance_amount),
            "stock_wip": wip_amount,
            "stock_variance": variance_amount,
        }

    def _create_journal_entry_from_map(self, je_map):
        """
        Given a journal entry map, create the Journal Entry record
        """
        accounts = self._get_accounting_data_for_valuation()
        wip_journal = accounts.get("wip_journal") or accounts["stock_journal"]
        posted = False
        move_lines = [
            self._prepare_account_move_line(accounts[account], amount, account)
            for account, amount in je_map.items()
            if amount
        ]
        if move_lines:
            je_vals = self._prepare_account_move_head(wip_journal)
            je_vals["line_ids"] = [(0, 0, x) for x in move_lines if x]
            je_new = self.env["account.move"].sudo().create(je_vals)
            je_new._post()
            posted = True
        return posted

    def clear_wip_journal_entries(self):
        """
        Clear the WIP accounts so that their balance is zero
        For non-stockable products, only WIP moves are cleared.
        For stockable products, all moves are reverted, as this
        is known to be needed for Manufacturing cases.
        """
        per_account_wip = {}
        total_wip = 0.0
        for je_line in self.mapped("account_move_ids.line_ids"):
            if je_line.product_id.type == "product" or je_line.is_wip_line:
                per_account_wip.setdefault(je_line.account_id, 0.0)
                per_account_wip[je_line.account_id] += je_line.balance
                total_wip += je_line.balance

        move_lines = [
            self._prepare_account_move_line(acc, -bal, "stock_wip")
            for acc, bal in per_account_wip.items()
            if not float_is_zero(bal, 6)
        ]
        if not float_is_zero(total_wip, 6):
            accounts = self._get_accounting_data_for_valuation()
            move_lines.append(
                self._prepare_account_move_line(accounts["stock_output"], total_wip)
            )
        if move_lines:
            wip_journal = accounts.get("wip_journal") or accounts["stock_journal"]
            je_vals = self._prepare_account_move_head(wip_journal)
            je_vals["line_ids"] = [(0, 0, x) for x in move_lines]
            je_new = self.env["account.move"].sudo().create(je_vals)
            je_new._post()

    def process_wip_and_variance(self, close=False):
        """
        For each Analytic Tracking Item with a Pending Amount different from zero,
        generate Journal Entries for WIP and excess Variances
        """
        all_tracking = self | self.child_ids
        if close:
            # Set to done, to have negative variances computed
            all_tracking.write({"state": "done"})
            # Before closing, ensure all WIP is posted
            self.process_wip_and_variance(close=False)
        for item in all_tracking:
            if close:
                je_map = item.clear_wip_journal_entries()
            else:
                wip_pending = round(
                    item.wip_actual_amount - item.wip_accounted_amount, 6
                )
                var_pending = round(
                    item.variance_actual_amount - item.variance_accounted_amount, 6
                )
                je_map = item._get_journal_entries_wip(wip_pending, var_pending)
            is_posted = item._create_journal_entry_from_map(je_map or {})
            if is_posted:
                # Update accounted amount to equal actual amounts
                item.accounted_amount = item.actual_amount
                item.wip_accounted_amount = item.wip_actual_amount
                item.variance_accounted_amount = item.variance_actual_amount
        if close:
            all_tracking.write({"state": "close"})

    def _cron_process_wip_and_variance(self):
        items = self.search([("state", "not in", ["close", "cancel"])])
        items.process_wip_and_variance()

    def action_cancel(self):
        # TODO: what to do if there are JEs done?
        all_tracking = self | self.child_ids
        all_tracking.write({"state": "cancel"})

    def _populate_abcost_tracking_item(self):
        to_calculate_with_childs = (self | self.child_ids).filtered("to_calculate")
        for tracking in to_calculate_with_childs:
            cost_rules = tracking.product_id.activity_cost_ids
            # Calculate Planned Amount if no ABC an only qty provided
            # or when a ABC tracking (sub)item is created
            if not tracking.planned_amount and not cost_rules:
                factor = tracking.activity_cost_id.factor or 1.0
                unit_cost = tracking.product_id.price_compute(
                    "standard_price", uom=tracking.product_id.uom_id
                )[tracking.product_id.id]
                qty = factor * (tracking.planned_qty or tracking.parent_id.planned_qty)
                tracking.planned_amount = qty * unit_cost
            # Generate ABC (sub)tracking items
            if cost_rules and not tracking.child_ids:
                for cost_rule in cost_rules:
                    vals = {
                        "parent_id": tracking.id,
                        "product_id": cost_rule.product_id.id,
                        "activity_cost_id": cost_rule.id,
                        "planned_qty": 0.0,
                    }
                    tracking.copy(vals)

    @api.model
    def create(self, vals):
        new = super().create(vals)
        new._populate_abcost_tracking_item()
        return new

    def write(self, vals):
        res = super().write(vals)
        # Write on planned_qty to update the planned amounts
        if vals.get("planned_qty"):
            self._populate_abcost_tracking_item()
        return res
