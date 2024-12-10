from odoo.fields import Command
from odoo.tests.common import TransactionCase, tagged


@tagged("-at_install", "post_install")
class TestAccountMoveUpdateAnalytic(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.line = cls.env["account.move.line"].search(
            [
                ("product_id", "!=", False),
                ("move_id.move_type", "=", "in_invoice"),
                ("move_id.state", "=", "posted"),
                ("analytic_distribution", "=", False),
            ],
            limit=1,
        )
        cls.plan = cls.env.ref("analytic.analytic_plan_projects")
        cls.account1 = cls.env["account.analytic.account"].search(
            [("plan_id", "=", cls.plan.id)], limit=1
        )
        cls.account2 = cls.env["account.analytic.account"].search(
            [("plan_id", "=", cls.plan.id), ("id", "!=", cls.account1.id)], limit=1
        )

    def test_analytic_line_created(self):
        """
        Test that changing analytic distribution recreates lines
        """
        wizard = (
            self.env["account.move.update.analytic.wizard"]
            .with_context(active_id=self.line.id)
            .create(
                {
                    "analytic_distribution": {str(self.account1.id): 100},
                }
            )
        )
        wizard.update_analytic_lines()
        self.assertEqual(self.line.analytic_line_ids.account_id, self.account1)
        wizard = (
            self.env["account.move.update.analytic.wizard"]
            .with_context(active_id=self.line.id)
            .create(
                {
                    "analytic_distribution": {str(self.account2.id): 100},
                }
            )
        )
        wizard.update_analytic_lines()
        self.assertEqual(self.line.analytic_line_ids.account_id, self.account2)

    def test_tax_distribution_added(self):
        """
        Test that changing analytic distribution on a line with a tax with analytic
        enabled changes the tax' analytic lines too, and splits tax lines if multiple
        lines have the same tax but a different analytic distribution
        """
        tax = self.env["account.tax"].search(
            [("type_tax_use", "=", "purchase")], limit=1
        )
        tax.analytic = True
        move = self.line.move_id.copy({"invoice_date": self.line.move_id.invoice_date})
        move.invoice_line_ids[1:].unlink()
        line1 = move.invoice_line_ids
        line1.write(
            {
                "tax_ids": [Command.set(tax.ids)],
                "analytic_distribution": {self.account1.id: 100},
            }
        )
        line2 = line1.copy({})
        line2.analytic_distribution = {self.account1.id: 100}
        move.action_post()
        self.assertEqual(line1.analytic_line_ids.account_id, self.account1)
        self.assertEqual(
            move.line_ids.filtered("tax_line_id").analytic_line_ids.account_id,
            self.account1,
        )
        wizard = (
            self.env["account.move.update.analytic.wizard"]
            .with_context(active_id=line1.id)
            .create(
                {
                    "analytic_distribution": {self.account2.id: 100},
                }
            )
        )
        wizard.update_analytic_lines()
        self.assertEqual(line1.analytic_line_ids.account_id, self.account2)
        self.assertEqual(line2.analytic_line_ids.account_id, self.account1)
        tax_lines = move.line_ids.filtered(lambda x: x.tax_line_id == tax)
        self.assertEqual(len(tax_lines), 2)
        self.assertEqual(
            len(list(filter(None, tax_lines.mapped("analytic_distribution")))), 2
        )
        self.assertItemsEqual(
            tax_lines.analytic_line_ids.account_id,
            self.account1 + self.account2,
        )
