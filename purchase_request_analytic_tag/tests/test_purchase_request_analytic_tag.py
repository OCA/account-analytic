# Copyright 2026 Escodoo
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import SUPERUSER_ID
from odoo.tests import common

from odoo.addons.base.tests.common import DISABLED_MAIL_CONTEXT


class TestPurchaseRequestAnalyticTag(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, **DISABLED_MAIL_CONTEXT))
        cls.purchase_request_obj = cls.env["purchase.request"]
        cls.purchase_request_line_obj = cls.env["purchase.request.line"]
        cls.wiz_obj = cls.env["purchase.request.line.make.purchase.order"]
        cls.supplier = cls.env.ref("base.res_partner_12")
        cls.product = cls.env.ref("product.product_product_13")
        cls.uom = cls.env.ref("uom.product_uom_unit")
        cls.picking_type = cls.env.ref("stock.picking_type_in")
        aa_tag_model = cls.env["account.analytic.tag"]
        cls.tag_1 = aa_tag_model.create({"name": "PR Tag 1"})
        cls.tag_2 = aa_tag_model.create({"name": "PR Tag 2"})

    def _create_request_with_tags(self, tags):
        request = self.purchase_request_obj.create(
            {
                "picking_type_id": self.picking_type.id,
                "requested_by": SUPERUSER_ID,
            }
        )
        line = self.purchase_request_line_obj.create(
            {
                "request_id": request.id,
                "product_id": self.product.id,
                "product_uom_id": self.uom.id,
                "product_qty": 3.0,
                "estimated_cost": 30.0,
                "analytic_tag_ids": [(6, 0, tags.ids)],
            }
        )
        request.button_to_approve()
        request.button_approved()
        return request, line

    def _make_purchase_order(self, line):
        wiz = self.wiz_obj.with_context(
            active_model="purchase.request.line",
            active_ids=[line.id],
            active_id=line.id,
        ).create({"supplier_id": self.supplier.id})
        wiz.make_purchase_order()
        return line.purchase_lines

    def test_line_stores_analytic_tags(self):
        _, line = self._create_request_with_tags(self.tag_1)
        self.assertIn(self.tag_1, line.analytic_tag_ids)

    def test_tags_propagate_to_purchase_order_line(self):
        _, line = self._create_request_with_tags(self.tag_1 + self.tag_2)
        po_lines = self._make_purchase_order(line)
        self.assertTrue(po_lines)
        self.assertIn(self.tag_1, po_lines.analytic_tag_ids)
        self.assertIn(self.tag_2, po_lines.analytic_tag_ids)

    def test_no_tags_no_propagation(self):
        request = self.purchase_request_obj.create(
            {
                "picking_type_id": self.picking_type.id,
                "requested_by": SUPERUSER_ID,
            }
        )
        line = self.purchase_request_line_obj.create(
            {
                "request_id": request.id,
                "product_id": self.product.id,
                "product_uom_id": self.uom.id,
                "product_qty": 2.0,
                "estimated_cost": 20.0,
            }
        )
        request.button_to_approve()
        request.button_approved()
        po_lines = self._make_purchase_order(line)
        self.assertTrue(po_lines)
        self.assertFalse(po_lines.analytic_tag_ids)
