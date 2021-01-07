# Copyright (C) 2020 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import api, fields, models


class AccountAnalyticLine(models.Model):
    _inherit = "account.analytic.line"

    parent_id = fields.Many2one(
        "account.analytic.line", "Parent Analytic Item", ondelete="cascade"
    )
    child_ids = fields.One2many(
        "account.analytic.line", "parent_id", string="Related Analytic Items"
    )
    activity_cost_rule_id = fields.Many2one(
        "activity.cost.rule", "Cost Rule Applied", ondelete="restrict"
    )

    def _match_activity_cost_rules_domain(self):
        """
        Return domain to find Activity Cost Rules
        matching an Analytic Item record.

        There is a match if:
        - The product used matches
        - The Analytic item has a related Project,
          and the rule has the "Has project" flag
        """
        self.ensure_one()
        domain = [("activity_product_id", "=", self.product_id.id)]
        if self.project_id:
            domain = ["|", ("has_project", "=", True)] + domain
        return domain

    def _prepare_activity_cost_data(self, rule):
        """
        Return a dict with the values to create
        a new Analytic item for a Cost Type
        """
        self.ensure_one()
        cost_product = rule.cost_type_product_id
        return {
            "name": "{} / {}".format(self.name, rule.name),
            "activity_cost_rule_id": rule.id,
            "product_id": cost_product.id,
            "unit_amount": self.unit_amount * rule.factor,
        }

    def _generate_activity_cost_lines(self):
        """
        Find applicable Activity Cost Rules
        and create Analytic Lines for each of them.

        This is done copying the original Analytic Item
        to ensure all other fields are preserved on the new Item.
        """
        for line in self:
            domain = line._match_activity_cost_rules_domain()
            cost_rules = self.env["activity.cost.rule"].search(domain)
            for rule in cost_rules:
                cost_vals = line._prepare_activity_cost_data(rule=rule)
                cost_vals["parent_id"] = line.id
                analytic_line = line.copy(cost_vals)
                analytic_line.on_change_unit_amount()

    @api.model
    def create(self, vals):
        res = super(AccountAnalyticLine, self).create(vals)
        res._generate_activity_cost_lines()
        return res

    def write(self, vals):
        """
        If Units are updated, also update the related cost Analytic Items
        """
        res = super(AccountAnalyticLine, self).write(vals)
        if vals.get("unit_amount"):
            for cost in self.mapped("child_ids"):
                cost_vals = self._prepare_activity_cost_data(
                    rule=cost.activity_cost_rule_id
                )
                cost.write(cost_vals)
                cost.on_change_unit_amount()
        return res
