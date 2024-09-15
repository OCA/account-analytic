# Copyright 2023 Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import Form, tagged

from odoo.addons.mrp_subcontracting.tests.common import TestMrpSubcontractingCommon


@tagged("post_install", "-at_install")
class TestMrpSubcontractingAnalytic(TestMrpSubcontractingCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.analytic_distribution = dict(
            {str(cls.env.ref("analytic.analytic_agrolait").id): 100.0}
        )

    def test_propagate_analytic_distribution(self):
        # Create a receipt picking from subcontractor
        picking_form = Form(self.env["stock.picking"])
        picking_form.picking_type_id = self.env.ref("stock.picking_type_in")
        picking_form.partner_id = self.subcontractor_partner1
        with picking_form.move_ids_without_package.new() as move:
            move.product_id = self.finished
            move.product_uom_qty = 1
        picking_receipt = picking_form.save()
        receipt_move = picking_receipt.move_ids
        receipt_move.analytic_distribution = self.analytic_distribution
        picking_receipt.action_confirm()
        production = (
            self.env["stock.move"]
            .search(
                [
                    ("product_id", "=", receipt_move.product_id.id),
                    ("move_dest_ids", "=", receipt_move.id),
                ]
            )
            .production_id
        )
        self.assertEqual(
            production.analytic_distribution, receipt_move.analytic_distribution
        )
        receipt_move.analytic_distribution = False
        self.assertEqual(production.analytic_distribution, False)
