# Copyright 2013 Julius Network Solutions
# Copyright 2015 Clear Corp
# Copyright 2016 OpenSynergy Indonesia
# Copyright 2017 ForgeFlow S.L.
# Copyright 2018 Hibou Corp.
# Copyright 2021 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests import Form, common


class TestStockPicking(common.TransactionCase):
    def setUp(self):
        super().setUp()

        self.valuation_account = self.env["account.account"].create(
            {
                "name": "Test stock valuation",
                "code": "tv",
                "user_type_id": self.env["account.account.type"].search([], limit=1).id,
                "reconcile": True,
                "company_id": self.env.ref("base.main_company").id,
            }
        )
        self.stock_input_account = self.env["account.account"].create(
            {
                "name": "Test stock input",
                "code": "tsti",
                "user_type_id": self.env["account.account.type"].search([], limit=1).id,
                "reconcile": True,
                "company_id": self.env.ref("base.main_company").id,
            }
        )
        self.stock_output_account = self.env["account.account"].create(
            {
                "name": "Test stock output",
                "code": "tout",
                "user_type_id": self.env["account.account.type"].search([], limit=1).id,
                "reconcile": True,
                "company_id": self.env.ref("base.main_company").id,
            }
        )
        self.stock_journal = self.env["account.journal"].create(
            {"name": "Stock Journal", "code": "STJTEST", "type": "general"}
        )
        self.analytic_tag_1 = self.env["account.analytic.tag"].create(
            {"name": "analytic tag test 1"}
        )
        self.analytic_tag_2 = self.env["account.analytic.tag"].create(
            {"name": "analytic tag test 2"}
        )
        self.analytic_account = self.env.ref("analytic.analytic_agrolait")
        self.warehouse = self.env.ref("stock.warehouse0")
        self.location = self.warehouse.lot_stock_id
        self.dest_location = self.env.ref("stock.stock_location_customers")
        self.outgoing_picking_type = self.env.ref("stock.picking_type_out")
        self.incoming_picking_type = self.env.ref("stock.picking_type_in")

        self.product_categ = self.env["product.category"].create(
            {
                "name": "Test category",
                "property_valuation": "real_time",
                "property_stock_valuation_account_id": self.valuation_account.id,
                "property_stock_account_input_categ_id": self.stock_input_account.id,
                "property_stock_account_output_categ_id": self.stock_output_account.id,
                "property_stock_journal": self.stock_journal.id,
            }
        )
        self.product = self.env["product.product"].create(
            {
                "name": "Test product",
                "type": "product",
                "categ_id": self.product_categ.id,
            }
        )
        std_price_wiz = Form(
            self.env["stock.change.standard.price"].with_context(
                active_id=self.product.id, active_model="product.product"
            )
        )
        std_price_wiz.new_price = 100
        wiz = std_price_wiz.save()
        wiz.change_price()

    def _create_picking(
        self,
        location_id,
        location_dest_id,
        picking_type_id,
        analytic_account_id=False,
        analytic_tag_ids=False,
    ):
        picking_form = Form(self.env["stock.picking"])
        picking_form.picking_type_id = picking_type_id
        picking_form.location_id = location_id
        picking_form.location_dest_id = location_dest_id
        with picking_form.move_ids_without_package.new() as move:
            move.product_id = self.product
            move.product_uom_qty = 1.0
            if analytic_account_id:
                move.analytic_account_id = analytic_account_id
            if analytic_tag_ids:
                for analytic_tag_id in analytic_tag_ids:
                    move.analytic_tag_ids.add(analytic_tag_id)
        picking = picking_form.save()
        picking.move_lines.quantity_done = 1.0
        picking.action_confirm()
        return picking

    def __update_qty_on_hand_product(self, product, new_qty):
        qty_wizard = self.env["stock.change.product.qty"].create(
            {
                "product_id": product.id,
                "product_tmpl_id": product.product_tmpl_id.id,
                "new_quantity": new_qty,
            }
        )
        qty_wizard.change_product_qty()

    def _confirm_picking_no_error(self, picking):
        picking.action_confirm()
        self.assertEqual(picking.state, "confirmed")

    def _force_assign_out_no_error(self, picking):
        self.assertEqual(picking.move_lines.reserved_availability, 0)
        picking.action_assign()
        self.assertEqual(picking.move_lines.reserved_availability, 1)
        self.assertEqual(picking.state, "assigned")

    def _picking_done_no_error(self, picking):
        picking.move_lines.quantity_done = 1.0
        picking.button_validate()
        self.assertEqual(picking.state, "done")

    def _check_account_move_no_error(self, picking):
        criteria1 = [
            ["ref", "=", "{} - {}".format(picking.name, picking.product_id.name)]
        ]
        acc_moves = self.env["account.move"].search(criteria1)
        self.assertGreater(len(acc_moves), 0)

    def _check_analytic_account_no_error(self, picking):
        move = picking.move_lines[0]
        criteria2 = [["move_id.ref", "=", picking.name]]
        acc_lines = self.env["account.move.line"].search(criteria2)
        for acc_line in acc_lines:
            if (
                acc_line.account_id
                != move.product_id.categ_id.property_stock_valuation_account_id
            ):
                self.assertEqual(
                    acc_line.analytic_account_id.id, move.analytic_account_id.id
                )
                self.assertEqual(
                    acc_line.analytic_tag_ids.ids, move.analytic_tag_ids.ids
                )

    def _check_no_analytic_account(self, picking):
        criteria2 = [
            ("move_id.ref", "=", picking.name),
            ("analytic_account_id", "!=", False),
        ]
        criteria3 = [
            ("move_id.ref", "=", picking.name),
            ("analytic_tag_ids", "not in", []),
        ]
        line_count = self.env["account.move.line"].search_count(criteria2)
        self.assertEqual(line_count, 0)
        line_count = self.env["account.move.line"].search_count(criteria3)
        self.assertEqual(line_count, 0)

    def test_outgoing_picking_with_analytic(self):
        picking = self._create_picking(
            self.location,
            self.dest_location,
            self.outgoing_picking_type,
            self.analytic_account,
            [self.analytic_tag_1, self.analytic_tag_2],
        )
        self.__update_qty_on_hand_product(self.product, 1)
        self._confirm_picking_no_error(picking)
        self._force_assign_out_no_error(picking)
        self._picking_done_no_error(picking)
        self._check_account_move_no_error(picking)
        self._check_analytic_account_no_error(picking)

    def test_outgoing_picking_without_analytic(self):
        picking = self._create_picking(
            self.location, self.dest_location, self.outgoing_picking_type,
        )
        self.__update_qty_on_hand_product(self.product, 1)
        self._confirm_picking_no_error(picking)
        self._force_assign_out_no_error(picking)
        self._picking_done_no_error(picking)
        self._check_account_move_no_error(picking)
        self._check_no_analytic_account(picking)

    def test_incoming_picking_with_analytic(self):
        picking = self._create_picking(
            self.location,
            self.dest_location,
            self.incoming_picking_type,
            self.analytic_account,
            [self.analytic_tag_1, self.analytic_tag_2],
        )
        self._confirm_picking_no_error(picking)
        self._picking_done_no_error(picking)
        self._check_account_move_no_error(picking)
        self._check_analytic_account_no_error(picking)
