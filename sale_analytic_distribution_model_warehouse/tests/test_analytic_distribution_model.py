# Copyright 2025 Tecnativa - Christian Ramos
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from lxml import etree

from odoo.addons.base.tests.common import BaseCommon


class TestAnalyticDistributionModel(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.model = cls.env["account.analytic.distribution.model"]

    def _get_view_arch(self, **kwargs):
        return etree.XML(self.model.get_view(**kwargs)["arch"])

    def test_get_view_list_adds_warehouse(self):
        arch = self._get_view_arch(view_type="list")
        self.assertTrue(arch.xpath("//field[@name='warehouse_id']"))

    def test_get_view_form_untouched(self):
        # The field is only injected in the list view
        arch = self._get_view_arch(view_type="form")
        self.assertFalse(arch.xpath("//field[@name='warehouse_id']"))

    def test_get_view_list_existing_warehouse(self):
        # A view already showing the field is returned as is, so the field is
        # not added a second time next to company_id
        view = self.env["ir.ui.view"].create(
            {
                "name": "Analytic Distribution Model list with warehouse",
                "model": self.model._name,
                "arch": """
                    <list>
                        <field name="warehouse_id"/>
                        <field name="company_id"/>
                    </list>
                """,
            }
        )
        arch = self._get_view_arch(view_id=view.id, view_type="list")
        self.assertEqual(len(arch.xpath("//field[@name='warehouse_id']")), 1)

    def test_get_view_list_without_company(self):
        # The field is anchored to company_id, so a view without it is left
        # untouched instead of failing
        view = self.env["ir.ui.view"].create(
            {
                "name": "Analytic Distribution Model list without company",
                "model": self.model._name,
                "arch": """
                    <list>
                        <field name="sequence"/>
                    </list>
                """,
            }
        )
        arch = self._get_view_arch(view_id=view.id, view_type="list")
        self.assertFalse(arch.xpath("//field[@name='warehouse_id']"))

    def test_get_applicable_fields(self):
        # The hook only exists when account_analytic_distribution_model_recalculate
        # is installed, which is not a dependency of this module
        if not self.env["ir.module.module"].search_count(
            [
                ("name", "=", "account_analytic_distribution_model_recalculate"),
                ("state", "=", "installed"),
            ],
            limit=1,
        ):
            self.skipTest(
                "account_analytic_distribution_model_recalculate is not installed"
            )
        self.assertIn("warehouse_id", self.model._get_applicable_fields())
