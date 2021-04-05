# Copyright 2015 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import fields
from odoo.tests import common


class TestPosAnalyticConfig(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.aml_obj = cls.env["account.move.line"]
        cls.pricelist = cls.env["product.pricelist"].create(
            {
                "name": "Test pricelist",
                "item_ids": [
                    (
                        0,
                        0,
                        {
                            "applied_on": "3_global",
                            "compute_price": "formula",
                            "base": "list_price",
                        },
                    )
                ],
            }
        )
        cls.main_config = cls.env.ref("point_of_sale.pos_config_main")
        cls.main_config.write(
            {
                "available_pricelist_ids": [(6, 0, cls.pricelist.ids)],
                "pricelist_id": cls.pricelist.id,
            }
        )
        cls.aa_01 = cls.env["account.analytic.account"].create(
            {"name": "Test Analytic Account"}
        )
        cls.customer_01 = cls.env["res.partner"].create({"name": "Mr. Odoo"})
        cls.product_01 = cls.env["product.product"].create({"name": "Test product"})
        cls.main_config.account_analytic_id = cls.aa_01
        cls.main_config.invoice_journal_id = cls.main_config.journal_id
        cls.session_01 = cls.env["pos.session"].create(
            {"config_id": cls.main_config.id}
        )
        cls.session_01.action_pos_session_open()
        payment_methods = cls.session_01.payment_method_ids
        account_receivable_id = (
            cls.env.user.partner_id.property_account_receivable_id.id
        )
        order_vals = {
            "id": "test-id-pos_analytic_by_config",
            "data": {
                "creation_date": "2021-04-05 12:00:00",
                "sequence_number": 1,
                "user_id": 1,
                "name": "Order test-id-pos_analytic_by_config",
                "uid": "test-id-pos_analytic_by_config",
                "partner_id": cls.customer_01.id,
                "pricelist_id": cls.pricelist.id,
                "fiscal_position_id": False,
                "pos_session_id": cls.session_01.id,
                "lines": [
                    (
                        0,
                        0,
                        {
                            "product_id": cls.product_01.id,
                            "qty": 1,
                            "price_unit": 10.0,
                            "price_subtotal": 10,
                            "price_subtotal_incl": 10,
                        },
                    )
                ],
                "amount_total": 10.0,
                "amount_tax": 0.0,
                "amount_paid": 10.0,
                "amount_return": 0.0,
                "statement_ids": [
                    [
                        0,
                        0,
                        {
                            "journal_id": cls.main_config.journal_id.id,
                            "amount": 10,
                            "name": fields.Datetime.now(),
                            "account_id": account_receivable_id,
                            "statement_id": cls.session_01.statement_ids[0].id,
                            "payment_method_id": payment_methods.filtered(
                                lambda pm: pm.is_cash_count
                                and not pm.split_transactions
                            )[0].id,
                        },
                    ]
                ],
            },
        }
        order = cls.env["pos.order"].create_from_ui([order_vals])
        cls.pos_order = cls.env["pos.order"].browse(order[0]["id"])
        cls.income_account = cls.session_01._prepare_line(cls.pos_order.lines)[
            "income_account_id"
        ]

    def test_order_simple_receipt(self):
        """Simple tickets are grouped by account in single move lines"""
        aml_domain = [
            ("account_id", "=", self.income_account),
            ("analytic_account_id", "=", self.aa_01.id),
        ]
        # There aren't lines with the analytic account yet
        self.assertFalse(self.aml_obj.search(aml_domain))
        self.session_01.action_pos_session_closing_control()
        # There they are
        self.assertEqual(len(self.aml_obj.search(aml_domain)), 1)

    def test_order_invoice(self):
        """Tickets with invoice are posted prior to session reconcilation"""
        aml_domain = [
            ("account_id", "=", self.income_account),
            ("product_id", "=", self.product_01.id),
            ("analytic_account_id", "=", self.aa_01.id),
        ]
        lines = self.aml_obj.search(aml_domain)
        # There aren't lines with the analytic account yet
        self.assertEqual(len(lines.ids), 0)
        self.pos_order.action_pos_order_invoice()
        lines = self.aml_obj.search(aml_domain)
        # There they are
        self.assertEqual(len(lines.ids), 1)
