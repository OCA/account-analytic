# Copyright 2017 PESOL (http://pesol.es) - Angel Moya (angel.moya@pesol.es)
# Copyright 2020 Tecnativa - Carlos Dauden
# Copyright 2020 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.exceptions import ValidationError
from odoo.tests.common import SavepointCase

from ..hooks import uninstall_hook


class TestAnalyticDimensionBase(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.dimension_obj = cls.env["account.analytic.dimension"]
        cls.tag_obj = cls.env["account.analytic.tag"]
        cls.analytic_line_obj = cls.env["account.analytic.line"]
        cls.dimension_1 = cls.dimension_obj.create(
            {"name": "Test dimension 1", "code": "test_dim_1"}
        )
        cls.dimension_2 = cls.dimension_obj.create(
            {"name": "Test dimension 2", "code": "test_dim_2"}
        )
        cls.analytic_tag_1a = cls.tag_obj.create(
            {"name": "Test tag 1A", "analytic_dimension_id": cls.dimension_1.id}
        )
        cls.analytic_tag_1b = cls.tag_obj.create(
            {"name": "Test tag 1B", "analytic_dimension_id": cls.dimension_1.id}
        )
        cls.analytic_tag_2a = cls.tag_obj.create(
            {"name": "Test tag 2A", "analytic_dimension_id": cls.dimension_2.id}
        )
        cls.analytic_account = cls.env["account.analytic.account"].create(
            {"name": "Test analytic account"}
        )
        cls.account = cls.env["account.account"].create(
            {
                "code": "test_dimension_acc_01",
                "name": "test dimension account",
                "user_type_id": cls.env.ref("account.data_account_type_receivable").id,
                "reconcile": True,
            }
        )
        cls.journal = cls.env["account.journal"].create(
            {"name": "Test  Journal", "code": "TJ", "type": "general"}
        )
        cls.partner = cls.env["res.partner"].create({"name": "Test_partner"})


class TestAnalyticDimensionCase(TestAnalyticDimensionBase):
    def test_analytic_dimension_spaces_error(self):
        """Test dimension creation with spaces in code."""
        dimension_error = {
            "name": "Test Spaces Error",
            "code": "test spaces error",
        }
        with self.assertRaises(ValidationError):
            self.dimension_obj.create(dimension_error)

    def test_analytic_entry_dimension(self):
        """Test dimension update on analytic entry creation"""
        line = self.analytic_line_obj.create(
            {
                "account_id": self.analytic_account.id,
                "name": "test",
                "tag_ids": [
                    (4, self.analytic_tag_1a.id),
                    (4, self.analytic_tag_2a.id),
                ],
            }
        )
        self.assertEqual(line.x_dimension_test_dim_1, self.analytic_tag_1a)
        self.assertEqual(line.x_dimension_test_dim_2, self.analytic_tag_2a)
        with self.assertRaises(ValidationError):
            line.write({"tag_ids": [(4, self.analytic_tag_1b.id)]})
        # Not allowed to change dimension of a tag if used
        with self.assertRaises(ValidationError):
            self.analytic_tag_1a.analytic_dimension_id = self.dimension_2.id
        # Empty tags - Using command 5
        line.write({"tag_ids": [(5,)]})
        self.assertFalse(line.x_dimension_test_dim_1)
        self.assertFalse(line.x_dimension_test_dim_2)
        # It should be allowed now
        self.analytic_tag_1a.analytic_dimension_id = self.dimension_2.id

    def test_account_entry_dimension(self):
        """Test dimension update on account move line creation"""
        move = self.env["account.move"].create(
            {
                "name": "/",
                "ref": "2011010",
                "journal_id": self.journal.id,
                "state": "draft",
            }
        )
        line = self.env["account.move.line"].create(
            {
                "name": "test",
                "account_id": self.account.id,
                "move_id": move.id,
                "analytic_account_id": self.analytic_account.id,
                "analytic_tag_ids": [
                    (4, self.analytic_tag_1a.id),
                    (4, self.analytic_tag_2a.id),
                ],
            }
        )
        self.assertEqual(line.x_dimension_test_dim_1, self.analytic_tag_1a)
        self.assertEqual(line.x_dimension_test_dim_2, self.analytic_tag_2a)
        with self.assertRaises(ValidationError):
            line.write({"analytic_tag_ids": [(4, self.analytic_tag_1b.id)]})
        # Not allowed to change dimension of a tag if used
        with self.assertRaises(ValidationError):
            self.analytic_tag_1a.analytic_dimension_id = self.dimension_2.id
        # Empty tags - Using command 6
        line.write({"analytic_tag_ids": [(6, 0, [])]})
        self.assertFalse(line.x_dimension_test_dim_1)
        self.assertFalse(line.x_dimension_test_dim_2)
        # It should be allowed now
        self.analytic_tag_1a.analytic_dimension_id = self.dimension_2.id

    def test_invoice_line_dimension(self):
        """Test dimension creation on account invoice line creation."""
        invoice = self.env["account.move"].create(
            {"journal_id": self.journal.id, "partner_id": self.partner.id}
        )
        line = self.env["account.move.line"].create(
            {
                "name": "test",
                "price_unit": 1,
                "account_id": self.account.id,
                "move_id": invoice.id,
                "analytic_account_id": self.analytic_account.id,
                "analytic_tag_ids": [
                    (4, self.analytic_tag_1a.id),
                    (4, self.analytic_tag_2a.id),
                ],
            }
        )
        self.assertEqual(line.x_dimension_test_dim_1, self.analytic_tag_1a)
        self.assertEqual(line.x_dimension_test_dim_2, self.analytic_tag_2a)
        with self.assertRaises(ValidationError):
            line.write({"analytic_tag_ids": [(4, self.analytic_tag_1b.id)]})
        # Not allowed to change dimension of a tag if used
        with self.assertRaises(ValidationError):
            self.analytic_tag_1a.analytic_dimension_id = self.dimension_2.id
        # Empty tags - Using commands 3 and 2
        line.write({"analytic_tag_ids": [(3, self.analytic_tag_1a.id)]})
        self.assertFalse(line.x_dimension_test_dim_1)
        line.write({"analytic_tag_ids": [(2, self.analytic_tag_2a.id)]})
        self.assertFalse(line.x_dimension_test_dim_2)
        # It should be allowed now
        self.analytic_tag_1a.analytic_dimension_id = self.dimension_2.id
        # Try command 0 for tags
        line.write(
            {
                "analytic_tag_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "Test tag 2B",
                            "analytic_dimension_id": self.dimension_2.id,
                        },
                    )
                ]
            }
        )
        self.assertTrue(line.x_dimension_test_dim_2)
        # Try command 1 for tags
        line.write(
            {
                "analytic_tag_ids": [
                    (
                        1,
                        line.analytic_tag_ids[0].id,
                        {"analytic_dimension_id": self.dimension_1.id},
                    )
                ]
            }
        )
        self.assertTrue(line.x_dimension_test_dim_1)
        self.assertFalse(line.x_dimension_test_dim_2)

    def test_remove_dimension(self):
        self.dimension_1.unlink()
        self.assertNotIn("x_dimension_test_dim_1", self.analytic_line_obj._fields)
        uninstall_hook(self.env.cr, False)
        self.assertNotIn("x_dimension_test_dim_2", self.analytic_line_obj._fields)

    def test_zz_dimension_rename(self):
        # It should executed the last one for avoiding side effects
        # as not everything is undone in this renaming
        self.dimension_1.write({"code": "test_renamed"})
        self.assertIn("x_dimension_test_renamed", self.analytic_line_obj._fields)
        self.assertIn("x_dimension_test_renamed", self.env["account.move.line"]._fields)
