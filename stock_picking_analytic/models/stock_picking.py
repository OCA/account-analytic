# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class StockPicking(models.Model):
    _name = "stock.picking"
    _inherit = ["stock.picking", "analytic.mixin"]

    original_analytic_distribution = fields.Json(
        help="Technical field. Use to store the value of"
        "analytic_distribution if there is no lines",
    )
    analytic_distribution = fields.Json(
        inverse="_inverse_analytic_distribution",
        states={
            "done": [("readonly", True)],
            "cancel": [("readonly", True)],
        },
    )
    # Assign a dummy search arg to the field to avoid triggering the warning.
    # Without this, use of move_ids_without_package in @api.depends() of the compute
    # method would trigger a warning from
    # https://github.com/odoo/odoo/blob/0f84366/odoo/fields.py#L808-L812
    # pylint: disable=method-search
    move_ids_without_package = fields.One2many(search="[]")

    # We use move_ids_without_package instead of move_ids throughout this method to
    # guarantee consistent behavior. i.e. the value of move_ids is available only after
    # the record has been saved.
    @api.depends(
        "move_ids_without_package.analytic_distribution",
        "original_analytic_distribution",
    )
    def _compute_analytic_distribution(self):
        """
        Get analytic account from first move and put it on picking
        """
        for picking in self:
            analytic_distribution = picking.original_analytic_distribution
            if picking.move_ids_without_package:
                analytic_distribution = picking.move_ids_without_package[
                    0
                ].analytic_distribution
                if any(
                    move.analytic_distribution != analytic_distribution
                    for move in picking.move_ids_without_package
                ):
                    analytic_distribution = False
            picking.analytic_distribution = analytic_distribution

    def _inverse_analytic_distribution(self):
        """
        If analytic distribution is set on picking, write it on all moves
        """
        for picking in self:
            if picking.analytic_distribution:
                picking.move_ids_without_package.write(
                    {"analytic_distribution": picking.analytic_distribution}
                )
            picking.original_analytic_distribution = picking.analytic_distribution
