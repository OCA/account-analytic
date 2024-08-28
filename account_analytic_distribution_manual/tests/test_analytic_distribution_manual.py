# Copyright 2024 Tecnativa - Carlos Lopez
# Copyright 2024 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from psycopg2.errors import UniqueViolation

from odoo.tests import tagged
from odoo.tools import mute_logger

from odoo.addons.account_analytic_distribution_manual.tests.common import (
    DistributionManualCommon,
)


@tagged("post_install", "-at_install")
class TestAnalyticDistributionManual(DistributionManualCommon):
    @mute_logger("odoo.sql_db")
    def test_copy_manual_distribution(self):
        distribution = self.distribution_1.copy()
        self.assertEqual(distribution.name, "Manual Distribution 1 (Copy)")
        distribution2 = self.distribution_1.copy({"name": "New name"})
        self.assertEqual(distribution2.name, "New name")
        with self.assertRaises(UniqueViolation):
            self.ManualDistribution.create(
                {
                    "name": "Manual Distribution 1",
                }
            )

    def test_manual_distribution_analytic_distribution_text(self):
        self.analytic_account_a1.name = "test-1"
        aa_1 = self.analytic_account_a1
        self.analytic_account_a2.name = "test-2"
        aa_2 = self.analytic_account_a2
        self.assertEqual(
            self.distribution_1.analytic_distribution_import,
            {"test-1": 40.0, "test-2": 60.0},
        )
        # Set analytic_distribution_import field
        self.distribution_1.analytic_distribution_import = {
            "test-1": 20.0,
            "test-2": 80.0,
        }
        self.assertEqual(
            self.distribution_1.analytic_distribution,
            {str(aa_1.id): 20.0, str(aa_2.id): 80.0},
        )
        # Remove aa_2
        self.distribution_1.analytic_distribution_import = {"test-1": 40.0}
        self.assertEqual(
            self.distribution_1.analytic_distribution, {str(aa_1.id): 40.0}
        )
        # Create aa_2 again
        self.distribution_1.analytic_distribution_import = {
            "test-1": 40.0,
            "test-2": 60.0,
        }
        self.assertEqual(
            self.distribution_1.analytic_distribution,
            {str(aa_1.id): 40.0, str(aa_2.id): 60.0},
        )
        # Update with an "incorrect name"
        self.distribution_1.analytic_distribution_import = {
            "test-1": 40.0,
            "test-3": 60.0,
        }
        self.assertEqual(
            self.distribution_1.analytic_distribution, {str(aa_1.id): 40.0}
        )
