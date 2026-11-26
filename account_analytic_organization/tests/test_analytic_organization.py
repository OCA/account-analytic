from odoo.tests.common import TransactionCase


class TestAnalyticOrganization(TransactionCase):
    def test_analytic_items_search_view(self):
        """The organization is available in the search of the Analytic Items"""
        view = self.env.ref("account.view_account_analytic_line_filter_inherit_account")
        arch = self.env["account.analytic.line"].get_view(view.id, "search")["arch"]
        self.assertIn('name="analytic_org"', arch)
        self.assertIn('name="group_by_analytic_org"', arch)
