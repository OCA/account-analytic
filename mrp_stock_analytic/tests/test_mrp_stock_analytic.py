# Copyright 2023 Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import Command
from odoo.exceptions import ValidationError
from odoo.tests import Form

from odoo.addons.stock_analytic.tests.test_stock_picking import CommonStockPicking


class TestMrpStockAnalytic(CommonStockPicking):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env.user.groups_id += cls.env.ref("analytic.group_analytic_accounting")
        cls.stock_location_id = cls.env["ir.model.data"]._xmlid_to_res_id(
            "stock.stock_location_stock"
        )
        cls.product_A = cls.env["product.product"].create(
            {
                "name": "Product A",
                "type": "consu",
                "categ_id": cls.product_categ.id,
                "standard_price": 10.0,
                "is_storable": True,
            }
        )
        cls.product_B = cls.env["product.product"].create(
            {
                "name": "Product B",
                "type": "consu",
                "categ_id": cls.product_categ.id,
                "standard_price": 10.0,
                "is_storable": True,
            }
        )
        cls.bom = cls.env["mrp.bom"].create(
            {
                "product_id": cls.product_A.id,
                "product_tmpl_id": cls.product_A.product_tmpl_id.id,
                "product_qty": 1.0,
                "bom_line_ids": [
                    Command.create({"product_id": cls.product_B.id, "product_qty": 1}),
                ],
            }
        )
        quants = (
            cls.env["stock.quant"]
            .with_context(inventory_mode=True)
            .create(
                {
                    "product_id": cls.product_B.id,
                    "inventory_quantity": 10,
                    "location_id": cls.stock_location_id,
                }
            )
        )
        quants.action_apply_inventory()
        cls.production = cls._create_production(2)
        cls.wip_account_id = cls.env.company.account_production_wip_account_id.id

    @classmethod
    def _create_production(cls, qty):
        production = cls.env["mrp.production"].create(
            {
                "product_id": cls.product_A.id,
                "bom_id": cls.bom.id,
                "product_qty": qty,
                "product_uom_id": cls.product_A.uom_id.id,
            }
        )
        production.action_confirm()
        mo_form = Form(production)
        mo_form.qty_producing = qty
        return mo_form.save()

    def _create_move(self, production, move_type="raw", **kwargs):
        if move_type == "raw":
            vals = {
                "name": self.product_B.name,
                "product_id": self.product_B.id,
                "product_uom_qty": 1,
                "product_uom": self.product_B.uom_id.id,
                "location_id": self.stock_location_id,
                "location_dest_id": production.production_location_id.id,
                "raw_material_production_id": production.id,
            }
        else:
            vals = {
                "name": self.product_A.name,
                "product_id": self.product_A.id,
                "product_uom_qty": 1,
                "product_uom": self.product_A.uom_id.id,
                "location_id": production.production_location_id.id,
                "location_dest_id": self.stock_location_id,
                "production_id": production.id,
            }
        vals.update(kwargs)
        return self.env["stock.move"].create(vals)

    def _action_wizard_form(self, open_record, action_res: dict) -> Form:
        context = dict(
            action_res.get("context", {}),
            active_model=open_record._name,
            active_ids=open_record.ids,
            active_id=open_record.id,
        )
        target = open_record.env[action_res["res_model"]].with_context(**context)
        return Form(target)

    def test_propagate_analytic_distribution(self):
        production = self.production
        self.assertEqual(len(production.move_raw_ids), 1)
        self.assertEqual(production.analytic_distribution, False)
        self.assertEqual(production.move_raw_ids[0].analytic_distribution, False)
        # Assign analytic distribution and it's propagated to component stock moves.
        production.analytic_distribution = self.analytic_distribution
        self.assertNotEqual(production.analytic_distribution, False)
        self.assertEqual(
            production.move_raw_ids[0].analytic_distribution,
            self.analytic_distribution,
        )
        # Remove analytic distribution and it's propagated to component stock moves.
        production.analytic_distribution = False
        self.assertEqual(production.move_raw_ids[0].analytic_distribution, False)

    def test_analytic_distribution_journal_items(self):
        production = self.production
        production.analytic_distribution = self.analytic_distribution
        self.assertNotEqual(production.analytic_distribution, False)
        production.button_mark_done()
        product_A_move_lines = (
            self.env["account.move"]
            .search([("stock_move_id", "=", production.move_finished_ids.id)])
            .line_ids
        )
        self.assertEqual(len(product_A_move_lines), 2)
        for move_line in product_A_move_lines:
            # No analytic distribution for journal items of the produced product.
            self.assertEqual(move_line.analytic_distribution, False)
        product_B_move_lines = (
            self.env["account.move"]
            .search([("stock_move_id", "=", production.move_raw_ids.id)])
            .line_ids
        )
        self.assertEqual(len(product_B_move_lines), 2)
        for move_line in product_B_move_lines:
            if move_line.account_id == self.valuation_account:
                self.assertEqual(move_line.analytic_distribution, False)
            else:
                self.assertEqual(
                    move_line.analytic_distribution, self.analytic_distribution
                )

    def test_propagate_analytic_to_finished_moves(self):
        self.env.company.mrp_analytic_on_finished = True
        production = self._create_production(1)
        production.analytic_distribution = self.analytic_distribution
        self.assertEqual(
            production.move_finished_ids.analytic_distribution,
            self.analytic_distribution,
        )
        production.analytic_distribution = False
        self.assertFalse(production.move_finished_ids.analytic_distribution)
        # When disabled, finished moves should not be updated.
        self.env.company.mrp_analytic_on_finished = False
        production2 = self._create_production(1)
        production2.analytic_distribution = self.analytic_distribution
        self.assertFalse(production2.move_finished_ids.analytic_distribution)

    def test_analytic_propagation_backorder(self):
        edit_production = Form(self.production)
        edit_production.qty_producing = 1
        production = edit_production.save()
        production.analytic_distribution = self.analytic_distribution
        self.assertNotEqual(production.analytic_distribution, False)
        quantity_issues = production._get_quantity_produced_issues()
        self.assertTrue(quantity_issues)
        backorder_action = production.button_mark_done()
        self.assertEqual(
            backorder_action.get("res_model"),
            "mrp.production.backorder",
        )
        backorder_wizard = self._action_wizard_form(production, backorder_action)
        backorder_wizard.save().action_backorder()
        action_view_backorders = production.action_view_mrp_production_backorders()
        backorder = (
            self.env["mrp.production"].search(action_view_backorders["domain"])
            - production
        )
        self.assertEqual(len(backorder), 1)
        self.assertEqual(
            backorder.analytic_distribution, production.analytic_distribution
        )
        self.assertEqual(
            backorder.move_raw_ids.analytic_distribution,
            backorder.analytic_distribution,
        )

    def test_wip_accounting_with_analytic_distribution(self):
        """Test analytic distribution flows from MO to WIP wizard lines and then
        to the created journal entries."""
        production = self.production
        production.analytic_distribution = self.analytic_distribution
        wizard = Form(
            self.env["mrp.account.wip.accounting"].with_context(
                active_ids=[production.id]
            )
        ).save()
        wip_line = wizard.line_ids.filtered(
            lambda line: line.account_id.id == self.wip_account_id
        )
        self.assertTrue(wip_line)
        self.assertEqual(wip_line.analytic_distribution, self.analytic_distribution)
        wizard.confirm()
        wip_move = self.env["account.move"].search(
            [
                ("wip_production_ids", "in", production.ids),
                ("reversed_entry_id", "=", False),
            ]
        )
        self.assertTrue(wip_move)
        wip_move_line = wip_move.line_ids.filtered(
            lambda line: line.account_id.id == self.wip_account_id
        )
        self.assertTrue(wip_move_line)
        self.assertEqual(
            wip_move_line.analytic_distribution, self.analytic_distribution
        )

    def test_wip_accounting_multi_analytic_distribution(self):
        """Test WIP wizard correctly groups MOs by analytic distribution and
        creates separate WIP journal lines with respective distributions."""
        # Create a second analytic account for a different distribution
        analytic_plan = self.env["account.analytic.plan"].create({"name": "Test Plan"})
        analytic_account_2 = self.env["account.analytic.account"].create(
            {"name": "Test Analytic 2", "plan_id": analytic_plan.id}
        )
        analytic_distribution_2 = {str(analytic_account_2.id): 100.0}
        # Create a second MO
        production_2 = self._create_production(3)
        # Assign different analytic distributions to each MO
        self.production.analytic_distribution = self.analytic_distribution
        production_2.analytic_distribution = analytic_distribution_2
        # Open WIP wizard with both MOs
        wizard = Form(
            self.env["mrp.account.wip.accounting"].with_context(
                active_ids=[self.production.id, production_2.id]
            )
        ).save()
        wip_lines = wizard.line_ids.filtered(
            lambda x: x.account_id.id == self.wip_account_id
        )
        # Two WIP debit lines, one per analytic distribution group
        self.assertEqual(len(wip_lines), 2)
        wip_distributions = wip_lines.mapped("analytic_distribution")
        self.assertIn(self.analytic_distribution, wip_distributions)
        self.assertIn(analytic_distribution_2, wip_distributions)
        # Non-WIP lines should have no analytic distribution
        non_wip_lines = wizard.line_ids - wip_lines
        for line in non_wip_lines:
            self.assertFalse(line.analytic_distribution)
        # Confirm and verify the journal entry
        wizard.confirm()
        wip_move = self.env["account.move"].search(
            [
                (
                    "wip_production_ids",
                    "in",
                    (self.production | production_2).ids,
                ),
                ("reversed_entry_id", "=", False),
            ]
        )
        self.assertEqual(len(wip_move), 1)
        wip_move_lines = wip_move.line_ids.filtered(
            lambda x: x.account_id.id == self.wip_account_id
        )
        self.assertEqual(len(wip_move_lines), 2)
        move_distributions = wip_move_lines.mapped("analytic_distribution")
        self.assertIn(self.analytic_distribution, move_distributions)
        self.assertIn(analytic_distribution_2, move_distributions)

    def test_mandatory_analytic_plan_validation(self):
        analytic_plan = self.env.ref("analytic.analytic_plan_projects")
        analytic_account = self.env["account.analytic.account"].create(
            {"name": "Test Manufacturing Project", "plan_id": analytic_plan.id}
        )
        self.env["account.analytic.applicability"].create(
            {
                "business_domain": "manufacturing_order",
                "analytic_plan_id": analytic_plan.id,
                "applicability": "mandatory",
            }
        )
        production = self._create_production(1)
        with self.assertRaisesRegex(ValidationError, "100% analytic distribution"):
            production.button_mark_done()
        production.analytic_distribution = {str(analytic_account.id): 50.0}
        with self.assertRaisesRegex(ValidationError, "100% analytic distribution"):
            production.button_mark_done()
        production.analytic_distribution = {str(analytic_account.id): 100.0}
        production.button_mark_done()
        self.assertEqual(production.state, "done")

    def test_new_component_analytic_on_create(self):
        production = self.production
        # No analytic on MO — new component should have none.
        self.assertFalse(production.analytic_distribution)
        new_move = self._create_move(production)
        self.assertFalse(new_move.analytic_distribution)
        # With analytic on MO — new component inherits it.
        production.analytic_distribution = self.analytic_distribution
        new_move = self._create_move(production)
        self.assertEqual(new_move.analytic_distribution, self.analytic_distribution)

    def test_new_finished_move_analytic_on_create(self):
        production = self._create_production(1)
        production.analytic_distribution = self.analytic_distribution
        # When enabled, new finished move inherits analytic.
        self.env.company.mrp_analytic_on_finished = True
        new_move = self._create_move(production, move_type="finished")
        self.assertEqual(new_move.analytic_distribution, self.analytic_distribution)
        # When disabled, new finished move gets no analytic.
        self.env.company.mrp_analytic_on_finished = False
        new_move = self._create_move(production, move_type="finished")
        self.assertFalse(new_move.analytic_distribution)

    def test_journal_items_with_finished_analytic_enabled(self):
        self.env.company.mrp_analytic_on_finished = True
        production = self._create_production(1)
        production.analytic_distribution = self.analytic_distribution
        production.button_mark_done()
        finished_move_lines = (
            self.env["account.move"]
            .search([("stock_move_id", "in", production.move_finished_ids.ids)])
            .line_ids
        )
        self.assertTrue(finished_move_lines)
        for move_line in finished_move_lines:
            if move_line.account_id == self.valuation_account:
                self.assertFalse(move_line.analytic_distribution)
            else:
                self.assertEqual(
                    move_line.analytic_distribution, self.analytic_distribution
                )
