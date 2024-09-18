# Copyright (C) 2019-Today: Odoo Community Association (OCA)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests import SavepointCase


class TestStockInvoiceOnshipping(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestStockInvoiceOnshipping, cls).setUpClass()
        cls.picking_model = cls.env["stock.picking"]
        cls.move_model = cls.env["stock.move"]
        cls.invoice_wizard = cls.env["stock.invoice.onshipping"]
        cls.invoice_model = cls.env["account.move"]
        cls.analytic_account_model = cls.env["account.analytic.account"]

        cls.partner = cls.env.ref("base.res_partner_2")
        cls.pick_type_out = cls.env.ref("stock.picking_type_out")
        cls.stock_location = cls.env.ref("stock.stock_location_stock")
        cls.customers_location = cls.env.ref("stock.stock_location_customers")
        cls.product = cls.env.ref("product.product_product_9")

        cls.analytic_account = cls.analytic_account_model.create(
            {
                "name": "Test Analytic Account",
            }
        )

    def test_get_invoice_line_values(self):
        picking = self.picking_model.create(
            {
                "partner_id": self.partner.id,
                "picking_type_id": self.pick_type_out.id,
                "location_id": self.stock_location.id,
                "location_dest_id": self.customers_location.id,
                "analytic_account_id": self.analytic_account.id,
            }
        )
        move_vals = {
            "product_id": self.product.id,
            "picking_id": picking.id,
            "location_dest_id": self.customers_location.id,
            "location_id": self.stock_location.id,
            "name": self.product.name,
            "product_uom_qty": 2,
            "product_uom": self.product.uom_id.id,
            "analytic_account_id": self.analytic_account.id,
        }
        new_move = self.move_model.create(move_vals)
        new_move.onchange_product_id()
        picking.set_to_be_invoiced()
        picking.action_confirm()
        picking.action_assign()
        for move in picking.move_ids_without_package:
            move.quantity_done = move.product_uom_qty
        picking.button_validate()
        wizard_obj = self.invoice_wizard.with_context(
            active_ids=picking.ids,
            active_model=picking._name,
            active_id=picking.id,
        )
        fields_list = wizard_obj.fields_get().keys()
        wizard_values = wizard_obj.default_get(fields_list)
        wizard = wizard_obj.create(wizard_values)
        wizard.onchange_group()
        wizard.action_generate()
        domain = [("picking_ids", "=", picking.id)]
        invoice = self.invoice_model.search(domain)

        for invoice_line in invoice.invoice_line_ids:
            self.assertEqual(
                invoice_line.analytic_account_id.id,
                picking.analytic_account_id.id,
            )
