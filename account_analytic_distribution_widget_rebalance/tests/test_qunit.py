# Copyright 2025 Camptocamp SA (https://www.camptocamp.com).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from pathlib import Path

from odoo.tests import HttpCase, tagged

from odoo.addons.web.tests.test_js import qunit_error_checker


@tagged("post_install", "-at_install")
class TestQUnit(HttpCase):
    def test_qunit(self):
        module_name = Path(__file__).parent.parent.name
        self.browser_js(
            f"/web/tests?module={module_name}",
            "",
            login="admin",
            timeout=1800,
            error_checker=qunit_error_checker,
        )
