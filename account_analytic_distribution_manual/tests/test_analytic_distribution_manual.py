# Copyright 2024 Tecnativa - Carlos Lopez
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
