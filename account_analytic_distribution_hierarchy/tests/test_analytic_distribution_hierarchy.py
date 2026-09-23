# Copyright 2026 Akretion - Raphael Valyi <raphael.valyi@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestAnalyticDistributionHierarchy(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # 1. Setup Single Plan
        cls.plan = cls.env["account.analytic.plan"].create(
            {
                "name": "Projects",
            }
        )

        # 2. Setup Parent and Child in the SAME plan
        cls.parent_account = cls.env["account.analytic.account"].create(
            {
                "name": "Project XY",
                "plan_id": cls.plan.id,
            }
        )
        cls.child_account = cls.env["account.analytic.account"].create(
            {
                "name": "Work Order A of Project XY",
                "plan_id": cls.plan.id,
                "parent_id": cls.parent_account.id,
            }
        )

        cls.account_revenue = cls.env["account.account"].create(
            {
                "name": "Revenue",
                "code": "REV01",
                "account_type": "income",
            }
        )

    def test_inject_parent_analytic_on_create(self):
        """Test that the parent account is injected when creating a Journal Entry."""
        move = self.env["account.move"].create(
            {
                "move_type": "entry",
                "date": "2026-01-01",
                "line_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "Revenue Line",
                            "account_id": self.account_revenue.id,
                            "credit": 100.0,
                            # User only provides the child account
                            "analytic_distribution": {
                                str(self.child_account.id): 100.0
                            },
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "name": "Counterpart",
                            "account_id": self.account_revenue.id,
                            "debit": 100.0,
                        },
                    ),
                ],
            }
        )

        line = move.line_ids.filtered(lambda line: line.credit > 0)

        # Verify both child and parent are now in the JSON distribution
        self.assertIn(str(self.child_account.id), line.analytic_distribution)
        self.assertIn(str(self.parent_account.id), line.analytic_distribution)

        # Verify the percentage was copied exactly
        self.assertEqual(line.analytic_distribution[str(self.parent_account.id)], 100.0)

    def test_inject_parent_analytic_on_write(self):
        """Test that the parent account is injected when updating an existing record."""
        move = self.env["account.move"].create(
            {
                "move_type": "entry",
                "date": "2026-01-01",
                "line_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "Revenue Line",
                            "account_id": self.account_revenue.id,
                            "credit": 100.0,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "name": "Counterpart",
                            "account_id": self.account_revenue.id,
                            "debit": 100.0,
                        },
                    ),
                ],
            }
        )

        line = move.line_ids.filtered(lambda line: line.credit > 0)

        # Update the analytic distribution post-creation (simulating UI interaction)
        line.write({"analytic_distribution": {str(self.child_account.id): 100.0}})

        # Verify the hook fired and injected the parent
        self.assertIn(str(self.child_account.id), line.analytic_distribution)
        self.assertIn(str(self.parent_account.id), line.analytic_distribution)
        self.assertEqual(line.analytic_distribution[str(self.parent_account.id)], 100.0)
