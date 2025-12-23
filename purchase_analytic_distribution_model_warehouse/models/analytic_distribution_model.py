# Copyright 2025 Tecnativa - Christian Ramos
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from lxml import etree

from odoo import api, fields, models


class AccountAnalyticDistributionModel(models.Model):
    _inherit = "account.analytic.distribution.model"

    warehouse_id = fields.Many2one(
        comodel_name="stock.warehouse",
        ondelete="cascade",
        check_company=True,
    )

    def _get_applicable_models(self, vals):
        vals = dict(vals or {})
        warehouse_id = self.env.context.get("warehouse_id", False)
        vals["warehouse_id"] = warehouse_id
        return super()._get_applicable_models(vals)

    @api.model
    def _get_default_search_domain_vals(self):
        res = super()._get_default_search_domain_vals()
        res.update({"warehouse_id": False})
        return res

    @api.model
    def get_view(self, view_id=None, view_type="form", **options):
        # Override to add warehouse_id field in list view to avoid
        # colisions when using this module together with
        # sale_analytic_by_warehouse module
        result = super().get_view(view_id=view_id, view_type=view_type, **options)
        if view_type == "list":
            doc = etree.XML(result["arch"])
            # Total company currency
            if doc.xpath("//field[@name='warehouse_id']"):
                return result
            node = doc.xpath("//field[@name='company_id']")
            if node:
                elem = etree.Element(
                    "field", {"name": "warehouse_id", "optional": "show"}
                )
                node[0].addprevious(elem)
                result["arch"] = etree.tostring(doc, encoding="unicode")
        return result
