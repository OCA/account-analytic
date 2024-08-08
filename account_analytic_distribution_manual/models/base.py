# Copyright 2024 Tecnativa - Carlos Lopez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import json

from lxml import etree

from odoo import api, models
from odoo.tools.misc import frozendict


class AnalyticMixin(models.AbstractModel):
    _inherit = "base"

    @api.model
    def get_view(self, view_id=None, view_type="form", **options):
        """
        The purpose of inheriting this method is to
        add a specific field, 'manual_distribution_id',
        to the tree/form views if the model has this field defined.

        Additionally, if a one2many field exists
        and the related model has the 'manual_distribution_id' field,
        the method will add the 'manual_distribution_id' field to the sub-view.

        Finally, the method returns the modified view.

        Note: This method should be inherited in the base model,
        not in the analytic.mixin model,
        to ensure it executes correctly for models
        that do not inherit from the mixin but have one2many fields.
        For example, when rendering account.move,
        it does not inherit from analytic.mixin,
        but it has one2many fields that inherit from analytic.mixin.
        """

        def add_field(node, view_type, res_model):
            attribute = "column_invisible" if view_type == "tree" else "invisible"
            modifiers = json.dumps({attribute: True})
            field_options = {
                "name": manual_distribution_field_name,
                "modifiers": modifiers,
            }
            field_element = etree.SubElement(node, "field", field_options)
            new_arch, new_models = View.postprocess_and_fields(field_element, res_model)
            _merge_view_fields(all_models, new_models)
            return field_element

        def model_has_field(model):
            return manual_distribution_field_name in self.env[model]._fields

        def _merge_view_fields(all_models, new_models):
            """Merge new_models into all_models. Both are {modelname(str) ➔ fields(tuple)}."""
            for model, view_fields in new_models.items():
                if model in all_models:
                    all_models[model] = tuple(set(all_models[model]) | set(view_fields))
                else:
                    all_models[model] = tuple(view_fields)

        result = super().get_view(view_id=view_id, view_type=view_type, **options)
        if view_type in ["tree", "form"]:
            View = self.env["ir.ui.view"]
            manual_distribution_field_name = "manual_distribution_id"
            all_models = result["models"].copy()  # {modelname(str) ➔ fields(tuple)}
            arch = etree.fromstring(result["arch"])
            if model_has_field(result.get("model")):
                root_node = arch.xpath(f"/{view_type}")
                for node in root_node:
                    add_field(node, view_type, result.get("model"))
            # check fields one2many
            for (res_model, field_list) in result["models"].items():
                for field_name in field_list:
                    if field_name not in self.env[res_model]._fields:
                        continue
                    field_def = self.env[res_model]._fields[field_name]
                    if field_def.type != "one2many":
                        continue
                    if not model_has_field(field_def.comodel_name):
                        continue
                    for sub_view_type in ["tree", "form"]:
                        xpath_expr = f"//field[@name='{field_name}']/{sub_view_type}"
                        sub_node = arch.xpath(xpath_expr)
                        for child_node in sub_node:
                            add_field(child_node, sub_view_type, field_def.comodel_name)
            result["arch"] = etree.tostring(arch, encoding="unicode")
            result["models"] = frozendict(all_models)
        return result
