# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from lxml import etree

from odoo import api, models


class IrUiView(models.Model):

    _inherit = "ir.ui.view"

    @api.model
    def _determine_in_tree_view(self, node):
        if node.tag in ("form", "tree"):
            if node.tag == "tree":
                return True
            if node.tag == "form":
                return False
        elif node.getparent() is not None:
            return self._determine_in_tree_view(node.getparent())
        return False

    @api.model
    def postprocess_and_fields(self, model, node, view_id):
        arch, fields = super(IrUiView, self).postprocess_and_fields(
            model, node, view_id
        )
        model_obj = self.env[model]
        if (
            hasattr(model_obj, "_add_dynamic_fields_in_views")
            and model_obj._add_dynamic_fields_in_views
        ):
            model_obj = self.env[model]
            eview = etree.fromstring(arch)
            view = self.browse([view_id])
            dimensions = self.env["account.analytic.dimension"].search([])
            dimensions_fields_name = [d.get_field_name() for d in dimensions]
            analytic_account_field_name = model_obj._analytic_account_field_name
            for field_name in dimensions_fields_name:
                new_field = model_obj.fields_get().get(field_name, False)
                if new_field:
                    if not view_id or view.type in ("form", "tree"):
                        xpath = "//field[@name='{}']".format(
                            analytic_account_field_name
                        )
                        for f_node in eview.xpath(xpath):
                            in_tree_view = self._determine_in_tree_view(f_node)
                            attrs = {
                                "name": field_name,
                                "readonly": "1",
                            }
                            if in_tree_view:
                                attrs["optional"] = "hide"
                            new_node = etree.Element("field", attrs)
                            f_node.addnext(new_node)
                            self.postprocess(
                                model, new_node, view_id, in_tree_view, fields
                            )
                    elif view.type == "search":
                        xpath = "//filter[@name='{}']".format(
                            analytic_account_field_name
                        )
                        for f_node in eview.xpath(xpath):
                            attrs = {
                                "name": field_name,
                                "string": new_field["string"],
                                "context": "{{'group_by': '{}'}}".format(field_name),
                            }
                            new_node = etree.Element("filter", attrs)
                            f_node.addnext(new_node)
                            self.postprocess(model, new_node, view_id, False, fields)
                    fields[field_name] = new_field
            arch = etree.tostring(eview)
        return arch, fields
