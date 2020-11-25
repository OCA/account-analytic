# Copyright 2017 PESOL (http://pesol.es) - Angel Moya (angel.moya@pesol.es)
# Copyright 2020 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from psycopg2 import sql

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class AccountAnalyticDimension(models.Model):
    _name = "account.analytic.dimension"
    _description = "Account Analytic Dimension"

    name = fields.Char(required=True)
    code = fields.Char(required=True)
    analytic_tag_ids = fields.One2many(
        comodel_name="account.analytic.tag",
        inverse_name="analytic_dimension_id",
        string="Analytic Tags",
    )

    @api.constrains("code")
    def _check_code(self):
        for dimension in self:
            if " " in dimension.code:
                raise ValidationError(_("Code can't contain spaces!"))

    @api.model
    def get_model_names(self):
        return [
            "account.move.line",
            "account.analytic.line",
            "account.invoice.report",
        ]

    def get_field_name(self, code=False):
        return "x_dimension_{}".format(code or self.code).lower()

    def _convert_dict_query(self, field_vals):
        val_query = [
            "{} = '{}'".format(key, field_val) for key, field_val in field_vals.items()
        ]
        vals = ", ".join(val_query)
        return vals

    def _update_invoice_report(self, field_to_update, value):
        self._cr.execute(
            sql.SQL(
                """ UPDATE {} SET {} WHERE id={} """.format(
                    field_to_update._table, value, field_to_update.id
                )
            )
        )
        field_to_update.invalidate_cache()

    @api.model
    def create(self, values):
        res = super().create(values)
        _models = self.env["ir.model"].search(
            [("model", "in", self.get_model_names())], order="id"
        )
        _models.write(
            {
                "field_id": [
                    (
                        0,
                        0,
                        {
                            "name": self.get_field_name(values["code"]),
                            "field_description": values.get("name"),
                            "ttype": "many2one",
                            "relation": "account.analytic.tag",
                        },
                    )
                ],
            }
        )
        return res

    def write(self, vals):
        field_vals = {}
        if "name" in vals or "code" in vals:
            if "name" in vals:
                field_vals["field_description"] = vals["name"]
            if "code" in vals:
                field_vals["name"] = self.get_field_name(vals["code"])
            for dimension in self:
                fields_to_update = self.env["ir.model.fields"].search(
                    [
                        ("model", "in", self.get_model_names()),
                        ("name", "=", dimension.get_field_name()),
                    ],
                    order="id",
                )
                # To avoid 'Can only rename one field at a time!'
                for field_to_update in fields_to_update:
                    if field_to_update.model == "account.invoice.report":
                        value = self._convert_dict_query(field_vals)
                        self._update_invoice_report(field_to_update, value)
                    else:
                        field_to_update.write(field_vals)
        return super().write(vals)

    def unlink(self):
        """Clean created fields before unlinking."""
        models = self.env["ir.model"].search([("model", "in", self.get_model_names())])
        for record in self:
            field_name = self.get_field_name(record.code)
            self.env["ir.model.fields"].search(
                [("model_id", "in", models.ids), ("name", "=", field_name)]
            ).unlink()
        return super().unlink()
