from odoo.tests import Form

from odoo.addons.base.tests.common import BaseCommon


class TestStockMove(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.analytic_account = cls.env["account.analytic.account"].create(
            {
                "name": "Maintenance",
                "plan_id": cls.env.ref("analytic.analytic_plan_projects").id,
            }
        )
        cls.maintenance_warehouse = cls.env["stock.warehouse"].create(
            {
                "name": "Test warehouse",
                "code": "TEST",
            }
        )
        cls.product = cls.env["product.product"].create(
            {
                "default_code": "TESTPROD",
                "name": "Test Product",
                "type": "consu",
                "is_storable": True,
                "uom_id": cls.env.ref("uom.product_uom_unit").id,
                "uom_po_id": cls.env.ref("uom.product_uom_unit").id,
            }
        )
        cls.equipment = cls.env["maintenance.equipment"].create(
            {
                "name": "Equipment",
                "allow_consumptions": True,
                "default_consumption_warehouse_id": cls.maintenance_warehouse.id,
            }
        )
        cls.request = cls.env["maintenance.request"].create(
            {
                "name": "Maintenance Request",
                "equipment_id": cls.equipment.id,
                "stage_id": cls.env.ref("maintenance.stage_1").id,
                "maintenance_team_id": cls.env.ref(
                    "maintenance.equipment_team_maintenance"
                ).id,
                "user_id": cls.env.ref("base.user_admin").id,
                "owner_user_id": cls.env.ref("base.user_admin").id,
            }
        )

    def _create_picking(self):
        action = self.request.action_view_stock_picking_ids()
        picking_form = Form(self.env["stock.picking"].with_context(**action["context"]))
        picking_form.picking_type_id = self.maintenance_warehouse.cons_type_id
        picking_form.location_id = self.maintenance_warehouse.lot_stock_id
        with picking_form.move_ids_without_package.new() as move:
            move.product_id = self.product
            move.product_uom_qty = 5
        return picking_form.save()

    def test_stock_move_inherits_equipment_distribution(self):
        self.equipment.analytic_distribution = {
            str(self.analytic_account.id): 100,
        }
        picking = self._create_picking()
        self.assertEqual(
            picking.move_ids.analytic_distribution,
            self.equipment.analytic_distribution,
        )

    def test_stock_move_without_distribution(self):
        self.equipment.analytic_distribution = False
        picking = self._create_picking()
        self.assertFalse(picking.move_ids.analytic_distribution)
