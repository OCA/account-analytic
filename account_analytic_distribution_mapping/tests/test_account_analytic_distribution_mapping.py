# Copyright 2026 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.exceptions import UserError, ValidationError
from odoo.tests.common import TransactionCase


class TestAnalyticDistributionMapping(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.dist_model = cls.env["account.analytic.distribution.model"]
        plan_model = cls.env["account.analytic.plan"]
        cls.account_model = cls.env["account.analytic.account"]
        cls.plan_1 = plan_model.create({"name": "plan_model 1"})
        cls.plan_2 = plan_model.create({"name": "plan_model 2"})
        cls.plan_3 = plan_model.create({"name": "plan_model 3"})
        cls.a1 = cls.account_model.create({"name": "A1", "plan_id": cls.plan_1.id})
        cls.a2 = cls.account_model.create({"name": "A2", "plan_id": cls.plan_2.id})
        cls.a2b = cls.account_model.create({"name": "A2b", "plan_id": cls.plan_2.id})
        cls.a3 = cls.account_model.create({"name": "A3", "plan_id": cls.plan_3.id})
        # a1 maps to a2 (plan_model 2) and a3 (plan_model 3)
        cls.a1.mapped_account_ids = cls.a2 | cls.a3

    def _as_sets(self, distribution):
        # Normalize distribution so assertions don't depend on key ordering
        return {
            frozenset(int(i) for i in key.split(",")): pct
            for key, pct in (distribution or {}).items()
        }

    def test_expands_distribution(self):
        # Check it expands on create
        rec = self.dist_model.create({"analytic_distribution": {str(self.a1.id): 100}})
        expected = {frozenset({self.a1.id, self.a2.id, self.a3.id}): 100}
        self.assertEqual(self._as_sets(rec.analytic_distribution), expected)
        # Check it expands on write
        rec2 = self.dist_model.create({})
        rec2.analytic_distribution = {str(self.a1.id): 100}
        self.assertEqual(self._as_sets(rec2.analytic_distribution), expected)
        # Check it expands on onchange
        rec3 = self.dist_model.new({"analytic_distribution": {str(self.a1.id): 100}})
        rec3._onchange_analytic_distribution_mapping()
        self.assertEqual(self._as_sets(rec3.analytic_distribution), expected)

    def test_plan_already_present_is_not_overwritten(self):
        # The line already fixes Plan 2 to a2b, so the a1->a2 mapping must not
        # add a second Plan 2 account, only the a1->a3 mapping applies
        key = f"{self.a1.id},{self.a2b.id}"
        record = self.dist_model.create({"analytic_distribution": {key: 100}})
        expected = {frozenset({self.a1.id, self.a2b.id, self.a3.id}): 100}
        self.assertEqual(self._as_sets(record.analytic_distribution), expected)

    def test_no_mapping_leaves_untouched(self):
        rec = self.dist_model.create({"analytic_distribution": {str(self.a2.id): 100}})
        expected = {frozenset({self.a2.id}): 100}
        self.assertEqual(self._as_sets(rec.analytic_distribution), expected)

    def test_mapping_is_direct_only(self):
        # a3 -> a2b would be a transitive hop from a1, it must not be followed
        self.a3.mapped_account_ids = self.a2b
        rec = self.dist_model.create({"analytic_distribution": {str(self.a1.id): 100}})
        expected = {frozenset({self.a1.id, self.a2.id, self.a3.id}): 100}
        self.assertEqual(self._as_sets(rec.analytic_distribution), expected)

    def test_unavailable_plan_is_not_added(self):
        # a1 maps to a2 (Plan 2) and a3 (Plan 3), making Plan 3 unavailable
        # must keep a3 out of the distribution while a2 is still in
        self.plan_3.default_applicability = "unavailable"
        rec = self.dist_model.create({"analytic_distribution": {str(self.a1.id): 100}})
        expected = {frozenset({self.a1.id, self.a2.id}): 100}
        self.assertEqual(self._as_sets(rec.analytic_distribution), expected)

    def test_skip_context_disables_expansion(self):
        skip = self.dist_model.with_context(skip_analytic_distribution_mapping=True)
        record = skip.create({"analytic_distribution": {str(self.a1.id): 100}})
        expected = {frozenset({self.a1.id}): 100}
        self.assertEqual(self._as_sets(record.analytic_distribution), expected)

    def test_same_root_plan_is_rejected(self):
        # Same root plan is rejected
        with self.assertRaises(ValidationError):
            self.a2.mapped_account_ids = self.a2b
        # Mapping per plan is rejected
        # a1 already maps to a2 (Plan 2), adding a2b (also Plan 2) must fail
        with self.assertRaises(ValidationError):
            self.a1.mapped_account_ids = self.a2 | self.a2b | self.a3

    def test_shared_account_maps_in_any_company(self):
        # A shared source account can only map to shared
        # accounts, and the mapping applies to documents of any company
        company_b = self.env["res.company"].create({"name": "AADM Company B"})
        self.env.user.company_ids = [(4, company_b.id)]
        shared_source = self.account_model.create(
            {
                "name": "Shared Src",
                "plan_id": self.plan_1.id,
                "company_id": False,
            }
        )
        shared_dest = self.account_model.create(
            {
                "name": "Shared Dest",
                "plan_id": self.plan_2.id,
                "company_id": False,
            }
        )
        dest_b = self.account_model.create(
            {
                "name": "Dest B",
                "plan_id": self.plan_2.id,
                "company_id": company_b.id,
            }
        )
        # Shared source cannot map to company-restricted records
        with self.assertRaises(UserError):
            shared_source.mapped_account_ids = dest_b
        # But it can map to shared records
        shared_source.mapped_account_ids = shared_dest
        record = (
            self.dist_model.with_context(allowed_company_ids=[company_b.id])
            .with_company(company_b)
            .create(
                {
                    "company_id": company_b.id,
                    "analytic_distribution": {str(shared_source.id): 100},
                }
            )
        )
        expected = {frozenset({shared_source.id, shared_dest.id}): 100}
        self.assertEqual(self._as_sets(record.analytic_distribution), expected)
