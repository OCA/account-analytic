# Copyright 2017 PESOL (http://pesol.es)
#                Angel Moya (angel.moya@pesol.es)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

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
    def _check_code_spaces(self):
        self.ensure_one()
        if " " in self.code:
            raise ValidationError(_("Code can't contain spaces!"))

    @api.model
    def create(self, values):
        res = super().create(values)
        model_names = (
            "account.move.line",
            "account.analytic.line",
            "account.invoice.report",
        )
        _models = self.env["ir.model"].search(
            [("model", "in", model_names)], order="id"
        )
        _models.write(
            {
                "field_id": [
                    (
                        0,
                        0,
                        {
                            "name": "x_dimension_{}".format(values.get("code")),
                            "field_description": values.get("name"),
                            "ttype": "many2one",
                            "relation": "account.analytic.tag",
                        },
                    )
                ]
            }
        )
        return res


class AccountAnalyticTag(models.Model):
    _inherit = "account.analytic.tag"

    analytic_dimension_id = fields.Many2one(
        comodel_name="account.analytic.dimension", string="Dimension"
    )

    def get_dimension_values(self):
        values = {}
        for tag in self.filtered("analytic_dimension_id"):
            code = tag.analytic_dimension_id.code
            values.update({"x_dimension_%s" % code: tag.id})
        return values

    def _check_analytic_dimension(self):
        tags_with_dimension = self.filtered("analytic_dimension_id")
        dimensions = tags_with_dimension.mapped("analytic_dimension_id")
        if len(tags_with_dimension) != len(dimensions):
            raise ValidationError(_("You can not set two tags from same dimension."))


class AnalyticDimensionLine(models.AbstractModel):
    _name = "analytic.dimension.line"
    _description = "Analytic Dimension Line"
    _analytic_tag_field_name = "analytic_tag_ids"

    def _handle_analytic_dimension(self):
        for adl in self:
            tag_ids = adl[self._analytic_tag_field_name]
            tag_ids._check_analytic_dimension()
            dimension_values = tag_ids.get_dimension_values()
            super(AnalyticDimensionLine, adl).write(dimension_values)

    @api.model_create_multi
    def create(self, values):
        result = super().create(values)
        analytic_tag_field_name = list(
            filter(lambda l: l.get(result._analytic_tag_field_name), values)
        )
        if analytic_tag_field_name:
            result._handle_analytic_dimension()
        return result

    def write(self, values):
        result = super().write(values)
        if values.get(self._analytic_tag_field_name):
            self._handle_analytic_dimension()
        return result


class AccountAnalyticLine(models.Model):
    _name = "account.analytic.line"
    _inherit = ["analytic.dimension.line", "account.analytic.line"]
    _analytic_tag_field_name = "tag_ids"


class AccountMoveLine(models.Model):
    _name = "account.move.line"
    _inherit = ["analytic.dimension.line", "account.move.line"]
    _analytic_tag_field_name = "analytic_tag_ids"
