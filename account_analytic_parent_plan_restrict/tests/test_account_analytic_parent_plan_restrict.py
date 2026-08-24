# Copyright 2026 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestAccountAnalyticParentPlanRestrict(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.account_obj = cls.env["account.analytic.account"]
        cls.plan_a = cls.env["account.analytic.plan"].create({"name": "Plan A"})
        cls.plan_b = cls.env["account.analytic.plan"].create({"name": "Plan B"})
        # grandparent -> parent -> child, all on plan A
        cls.grandparent = cls.account_obj.create(
            {
                "name": "grandparent",
                "plan_id": cls.plan_a.id,
            }
        )
        cls.parent = cls.account_obj.create(
            {
                "name": "parent",
                "plan_id": cls.plan_a.id,
                "parent_id": cls.grandparent.id,
            }
        )
        cls.child = cls.account_obj.create(
            {
                "name": "child",
                "plan_id": cls.plan_a.id,
                "parent_id": cls.parent.id,
            }
        )

    def test_plan_mismatch_on_child_create(self):
        with self.assertRaises(ValidationError):
            self.account_obj.create(
                {
                    "name": "bad child",
                    "plan_id": self.plan_b.id,
                    "parent_id": self.parent.id,
                }
            )

    def test_plan_mismatch_on_child_write(self):
        with self.assertRaises(ValidationError):
            self.child.write({"plan_id": self.plan_b.id})

    def test_plan_mismatch_on_parent_write(self):
        # Changing intermediate node plan must be rejected, it would break
        # consistency with parent and child
        with self.assertRaises(ValidationError):
            self.parent.write({"plan_id": self.plan_b.id})

    def test_plan_consistent_write_allowed(self):
        # Moving a whole subtree onto another parent that shares plan is fine
        other_root = self.account_obj.create(
            {
                "name": "other root",
                "plan_id": self.plan_a.id,
            }
        )
        self.grandparent.write({"parent_id": other_root.id})
        self.assertEqual(self.grandparent.parent_id, other_root)
