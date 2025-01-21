# Copyright 2017 PESOL (http://pesol.es) - Angel Moya (angel.moya@pesol.es)
# Copyright 2020 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from lxml import etree

from odoo import api, models


class AccountMoveLine(models.Model):
    _name = "account.move.line"
    _inherit = ["analytic.dimension.line", "account.move.line"]
    _analytic_tag_field_name = "analytic_tag_ids"

    @api.model
    def _add_dimension_filters(self, res):
        arch = etree.fromstring(res["arch"])
        node_search = arch.xpath("//field[@name='journal_id']")
        node_filter = arch.xpath("//filter[@name='groupby_date']")
        for dimension in self.env["account.analytic.dimension"].search([]):
            fieldname = dimension.get_field_name()
            if node_search:
                elem = etree.Element(
                    "field",
                    {
                        "name": fieldname,
                        "string": dimension.name,
                        "domain": "[('analytic_dimension_id', '=', %d)]" % dimension.id,
                    },
                )
                node_search[0].addnext(elem)
            if node_filter:
                elem = etree.Element(
                    "filter",
                    {
                        "name": "groupby_%s" % fieldname,
                        "string": dimension.name,
                        "domain": "[]",
                        "context": "{'group_by' : '%s'}" % fieldname,
                    },
                )
                node_filter[0].addnext(elem)
        res["arch"] = etree.tostring(arch)
        return res

    @api.model
    def fields_view_get(
        self, view_id=None, view_type="form", toolbar=False, submenu=False
    ):
        """Inject dimension fields in search views."""
        res = super().fields_view_get(
            view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu
        )
        if view_type == "search":
            res = self._add_dimension_filters(res)
        return res
