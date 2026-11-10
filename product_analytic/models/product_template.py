from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    analytic_distribution_model_ids = fields.One2many(
        "account.analytic.distribution.model",
        string="Analytic Distribution Models",
        compute="_compute_analytic_distribution_models",
        inverse="_inverse_analytic_distribution_models",
    )

    @api.depends(
        "product_variant_ids", "product_variant_ids.analytic_distribution_model_ids"
    )
    def _compute_analytic_distribution_models(self):
        for tmpl in self:
            tmpl.analytic_distribution_model_ids = (
                tmpl.product_variant_id.analytic_distribution_model_ids
            )

    def _inverse_analytic_distribution_models(self):
        for tmpl in self:
            if tmpl.product_variant_count > 1:
                continue
            product_variant = tmpl.product_variant_id
            product_variant.analytic_distribution_model_ids = (
                tmpl.analytic_distribution_model_ids
            )

    @api.model_create_multi
    def create(self, vals_list):
        templates = super().create(vals_list)
        for template, vals in zip(templates, vals_list, strict=False):
            distribution_cmds = vals.get("analytic_distribution_model_ids", False)
            if not distribution_cmds or template.product_variant_count > 1:
                continue
            product_variant = template.product_variant_id
            product_variant.write(
                {
                    "analytic_distribution_model_ids": distribution_cmds,
                }
            )
        return templates
