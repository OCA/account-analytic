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
    analytic_distribution = fields.Json(inverse="_inverse_analytic_distribution")

    @api.depends(
        "move_ids_without_package.analytic_distribution",
        "original_analytic_distribution",
    )
    def _compute_analytic_distribution(self):
        """
        Get analytic account from first move and put it on picking
        """
        if not self.filtered("id"):
            return
        self.flush_model(["move_ids", "original_analytic_distribution"])
        self.env["stock.move"].flush_model(["analytic_distribution"])
        self.env.cr.execute(
            """
            SELECT
                picking.id,
                CASE
                    WHEN
                        COUNT(move.id) = 0
                        THEN picking.original_analytic_distribution
                    WHEN
                        COUNT(DISTINCT move.analytic_distribution) = 1
                        THEN (
                            ARRAY_AGG(move.analytic_distribution)
                            FILTER (WHERE move.analytic_distribution IS NOT NULL)
                        )[1]
                END AS analytic_distribution
            FROM
                stock_picking AS picking
            LEFT JOIN
                stock_move AS move
                ON picking.id = move.picking_id
            WHERE
                picking.id IN %s
            GROUP BY
                picking.id;
            """,
            [tuple(self.ids)],
        )
        result = dict(self.env.cr.fetchall())
        for picking in self:
            picking.analytic_distribution = result.get(picking.id)

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
