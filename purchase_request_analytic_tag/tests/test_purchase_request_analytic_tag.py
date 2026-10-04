# Copyright 2025 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import SUPERUSER_ID
from odoo.tests import common

from odoo.addons.base.tests.common import DISABLED_MAIL_CONTEXT


class TestPurchaseRequestAnalyticTag(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, **DISABLED_MAIL_CONTEXT))

        cls.wiz = cls.env["purchase.request.line.make.purchase.order"]
        cls.plan = cls.env["account.analytic.plan"].create(
            {
                "name": "Projects Plan",
            }
        )
        cls.analytic_account_1 = cls.env["account.analytic.account"].create(
            {
                "name": "Test account 1",
                "plan_id": cls.plan.id,
            },
        )
        aa_tag_model = cls.env["account.analytic.tag"]
        cls.analytic_tag_1 = aa_tag_model.create({"name": "Test tag 1"})
        cls.analytic_tag_2 = aa_tag_model.create({"name": "Test tag 2"})

        # Prepare purchase request
        vals = {
            "picking_type_id": cls.env.ref("stock.picking_type_in").id,
            "requested_by": SUPERUSER_ID,
        }
        cls.purchase_request = cls.env["purchase.request"].create(vals)
        vals = {
            "request_id": cls.purchase_request.id,
            "product_id": cls.env.ref("product.product_product_13").id,
            "product_uom_id": cls.env.ref("uom.product_uom_unit").id,
            "product_qty": 5.0,
        }
        cls.purchase_request_line = cls.env["purchase.request.line"].create(vals)

    def test_01_purchase_request_without_tags(self):
        self.assertFalse(self.purchase_request_line.analytic_tag_ids)
        self.assertFalse(self.purchase_request_line.purchase_lines)
        self.purchase_request.button_to_approve()
        self.purchase_request.button_approved()
        vals = {"supplier_id": self.env.ref("base.res_partner_12").id}
        wiz_id = self.wiz.with_context(
            active_model="purchase.request.line",
            active_ids=[self.purchase_request_line.id],
            active_id=self.purchase_request_line.id,
        ).create(vals)
        wiz_id.make_purchase_order()

        po_line = self.purchase_request_line.purchase_lines
        self.assertTrue(po_line)
        self.assertFalse(po_line.analytic_tag_ids)

    def test_02_purchase_request_with_tags(self):
        self.purchase_request_line.analytic_distribution = {
            self.analytic_account_1.id: 100
        }
        self.purchase_request_line.analytic_tag_ids = self.analytic_tag_1

        self.purchase_request.button_to_approve()
        self.purchase_request.button_approved()

        vals = {"supplier_id": self.env.ref("base.res_partner_12").id}
        wiz_id = self.wiz.with_context(
            active_model="purchase.request.line",
            active_ids=[self.purchase_request_line.id],
            active_id=self.purchase_request_line.id,
        ).create(vals)
        wiz_id.make_purchase_order()

        po_line = self.purchase_request_line.purchase_lines
        self.assertEqual(
            self.purchase_request_line.analytic_distribution,
            po_line.analytic_distribution,
        )
        self.assertEqual(
            self.purchase_request_line.analytic_tag_ids, po_line.analytic_tag_ids
        )

    def test_03_purchase_request_with_multi_tags(self):
        self.purchase_request_line.analytic_distribution = {
            self.analytic_account_1.id: 100
        }
        self.purchase_request_line.analytic_tag_ids = (
            self.analytic_tag_1 + self.analytic_tag_2
        )

        self.purchase_request.button_to_approve()
        self.purchase_request.button_approved()

        vals = {"supplier_id": self.env.ref("base.res_partner_12").id}
        wiz_id = self.wiz.with_context(
            active_model="purchase.request.line",
            active_ids=[self.purchase_request_line.id],
            active_id=self.purchase_request_line.id,
        ).create(vals)
        wiz_id.make_purchase_order()

        po_line = self.purchase_request_line.purchase_lines
        self.assertEqual(
            self.purchase_request_line.analytic_distribution,
            po_line.analytic_distribution,
        )
        self.assertEqual(
            self.purchase_request_line.analytic_tag_ids, po_line.analytic_tag_ids
        )
