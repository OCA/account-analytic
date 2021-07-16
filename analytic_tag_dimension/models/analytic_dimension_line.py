# Copyright 2017 PESOL (http://pesol.es) - Angel Moya (angel.moya@pesol.es)
# Copyright 2020 Tecnativa - Carlos Dauden
# Copyright 2021 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class AnalyticDimensionLine(models.AbstractModel):
    _name = "analytic.dimension.line"
    _description = "Analytic Dimension Line"
    _analytic_tag_field_name = "analytic_tag_ids"

    def _reflect(self):
        """If the model is populated after the dimension is created, the dimension
        fields won't be present, so we need to inject them here.
        """
        super()._reflect()
        context = self.env.context
        if self._inherit == self._name or context.get("overpass_dim_creation"):
            return
        field_obj = self.env["ir.model.fields"]
        models = self._inherit
        if isinstance(self._inherit, str):
            models = [self._inherit]
        dimensions = self.env["account.analytic.dimension"].search([])
        field_names = [x.get_field_name(x.code) for x in dimensions]
        fields_inherit = field_obj.search(
            [("model_id.model", "in", models), ("name", "in", field_names)]
        )
        model = self.env["ir.model"].search([("model", "=", self._name)])
        for field in fields_inherit:
            if not field_obj.search(
                [("model_id", "=", model.id), ("name", "=", field.name)]
            ):
                field.with_context(overpass_dim_creation=True).copy(
                    {"model_id": model.id}
                )

    def _handle_analytic_dimension(self, vals):
        Tag = self.env["account.analytic.tag"]
        field = self._analytic_tag_field_name
        tags = self[field]
        vals = vals.copy()
        prev_dim_vals = tags.get_dimension_values()
        if vals.get(field):
            new_commands = []
            for command in vals.get(field):
                if command[0] == 0:
                    tag = Tag.create(command[2])
                    tags += tag
                    new_commands.append((4, tag.id))
                elif command[0] == 1:
                    tag = Tag.browse(command[1])
                    tag.write(command[2])
                    tags |= tag
                    new_commands.append((4, tag.id))
                else:
                    new_commands.append(command)
                    if command[0] == 2:
                        tags -= Tag.browse(command[1])
                    elif command[0] == 3:
                        tags -= Tag.browse(command[1])
                    elif command[0] == 4:
                        tags += Tag.browse(command[1])
                    elif command[0] == 5:
                        tags = Tag
                    elif command[0] == 6:
                        tags = Tag.browse(command[2])
            vals[field] = new_commands
        else:
            tags = Tag
        tags._check_analytic_dimension()
        current_dim_vals = tags.get_dimension_values()
        # Add explicit False assignation to removed tags
        for key in prev_dim_vals:
            if key not in current_dim_vals:
                current_dim_vals[key] = False
        vals.update(current_dim_vals)
        return vals

    @api.model_create_multi
    def create(self, vals_list):
        """Inject values for dimension fields."""
        new_vals_list = []
        for vals in vals_list:
            if self._analytic_tag_field_name in vals:
                vals = self._handle_analytic_dimension(vals)
            new_vals_list.append(vals)
        return super().create(new_vals_list)

    def write(self, vals):
        """Inject values for dimension fields."""
        if self._analytic_tag_field_name in vals:
            for record in self:
                vals = record._handle_analytic_dimension(vals)
                super(AnalyticDimensionLine, record).write(vals)
            return True
        return super().write(vals)
