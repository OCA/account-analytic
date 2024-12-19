# Copyright 2024 (APSL - Nagarro) Bernat Obrador
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged("post_install", "-at_install")
class TestTrialAnalyticBalanceReport(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.account_type_map = cls.env[
            "report.account_analytic_report.trial_balance_analytic"
        ]._get_account_type_mapping()

        cls.analytic_plan_1 = cls.env["account.analytic.plan"].create(
            {
                "name": "Plan 1",
            }
        )
        account_group = cls.env["account.group"]
        cls.group5 = account_group.create({"code_prefix_start": "5", "name": "Group 5"})
        cls.group4 = account_group.create({"code_prefix_start": "4", "name": "Group 4"})
        cls.group42 = account_group.create(
            {"code_prefix_start": "42", "name": "Group 4", "parent_id": cls.group4.id}
        )

        cls.expense_account = cls.env["account.account"].create(
            {
                "name": "Expenses Account",
                "code": "5000",
                "account_type": "expense",
                "company_id": cls.env.user.company_id.id,
                "group_id": cls.group5.id,
            }
        )
        cls.income_account = cls.env["account.account"].create(
            {
                "name": "Income Account",
                "code": "4000",
                "account_type": "income",
                "company_id": cls.env.user.company_id.id,
                "group_id": cls.group4.id,
            }
        )
        cls.income_account_2 = cls.env["account.account"].create(
            {
                "name": "Income Account 2",
                "code": "4200",
                "account_type": "income",
                "company_id": cls.env.user.company_id.id,
                "group_id": cls.group42.id,
            }
        )

        cls.aaa_1 = cls.env["account.analytic.account"].create(
            {"name": "Account 1", "plan_id": cls.analytic_plan_1.id}
        )

        cls.aaa_2 = cls.env["account.analytic.account"].create(
            {"name": "Account 2", "plan_id": cls.analytic_plan_1.id}
        )
        cls.account_field = cls.analytic_plan_1._column_name()
        cls.aal_1 = cls.env["account.analytic.line"].create(
            {
                "name": "aal 1",
                "code": "aal1",
                cls.account_field: cls.aaa_1.id,
                "general_account_id": cls.expense_account.id,
                "amount": -150.0,
                "date": "2024-09-30",
            }
        )
        cls.aal_2 = cls.env["account.analytic.line"].create(
            {
                "name": "aal 2",
                "code": "aal2",
                cls.account_field: cls.aaa_2.id,
                "general_account_id": cls.expense_account.id,
                "amount": -50,
                "date": "2024-11-30",
            }
        )
        cls.aal_3 = cls.env["account.analytic.line"].create(
            {
                "name": "aal 3",
                "code": "aal3",
                cls.account_field: cls.aaa_2.id,
                "general_account_id": cls.income_account.id,
                "amount": 250,
                "date": "2024-12-31",
            }
        )

        cls.date_from = "2024-10-01"
        cls.date_to = "2024-12-31"
        cls.fy_start_date = "2024-01-01"

    def _get_report_lines(
        self,
        account_ids=False,
        show_hierarchy=False,
        group_by_analytic_account=False,
        financial_account_ids=None,
    ):
        company = self.env.user.company_id
        trial_analytic_balance = self.env["ac.trial.balance.report.wizard"].create(
            {
                "date_from": self.date_from,
                "date_to": self.date_to,
                "show_hierarchy": show_hierarchy,
                "company_id": company.id,
                "account_ids": account_ids,
                "fy_start_date": self.fy_start_date,
                "plan_id": self.analytic_plan_1.id,
                "group_by_analytic_account": group_by_analytic_account,
                "account_account_ids": financial_account_ids,
            }
        )
        data = trial_analytic_balance._prepare_report_trial_balance_analytic()
        res_data = self.env[
            "report.account_analytic_report.trial_balance_analytic"
        ]._get_report_values(trial_analytic_balance, data)
        return res_data

    def _accounts_in_report(self, trial_balance):
        accounts_in_report = []
        for account in trial_balance:
            accounts_in_report.append(account["id"])

        return accounts_in_report

    def _check_total_amounts_by_acc_type(
        self, totals_by_acc_type, include_both_accounts=False
    ):
        for type_name, total_by_acc_type in totals_by_acc_type.items():
            if type_name == self.account_type_map["expense"]:
                self.assertTrue(total_by_acc_type["total_initial_balance"] == -150)
                self.assertTrue(total_by_acc_type["total_ending_balance"] == -200)

                if include_both_accounts:
                    for aaa_id, amount in total_by_acc_type[
                        "total_period_balance"
                    ].items():
                        if aaa_id == self.aaa_2.id:
                            self.assertEqual(amount, -50)
                        else:
                            self.assertEqual(amount, 0)
                else:
                    self.assertTrue(total_by_acc_type["total_period_balance"] == -50)
            elif type_name == self.account_type_map["income"]:
                self.assertTrue(total_by_acc_type["total_initial_balance"] == 0)
                self.assertTrue(total_by_acc_type["total_ending_balance"] == 250)
                if include_both_accounts:
                    for aaa_id, amount in total_by_acc_type[
                        "total_period_balance"
                    ].items():
                        if aaa_id == self.aaa_2.id:
                            self.assertEqual(amount, 250)
                        else:
                            self.assertEqual(amount, 0)
                else:
                    self.assertTrue(total_by_acc_type["total_period_balance"] == 250)

    def test01_trial_analytic_balance(self):
        res_data = self._get_report_lines()
        trial_analytic_balance = res_data["trial_balance"]
        accounts_in_report = self._accounts_in_report(trial_analytic_balance)
        totals = res_data["total_amounts"]

        self.assertTrue(len(accounts_in_report) == 2)
        self.assertTrue(self.expense_account.id in accounts_in_report)
        self.assertTrue(self.income_account.id in accounts_in_report)
        self.assertFalse(self.income_account_2.id in accounts_in_report)

        # Checks total amounts by account type
        self._check_total_amounts_by_acc_type(res_data["totals_by_acc_type"])

        # Checks total amounts
        self.assertEqual(totals["total_initial_balance"], -150)
        self.assertEqual(totals["total_period_balance"], -50 + 250)
        self.assertEqual(
            totals["total_ending_balance"],
            -150 + -50 + 250,
        )

        # Check balances for every account
        for account in trial_analytic_balance:
            if account["id"] == self.income_account.id:
                self.assertEqual(account["initial_balance"], 0)
                self.assertEqual(account["balance"], 250)
                self.assertEqual(account["ending_balance"], 250)
            else:
                self.assertEqual(account["initial_balance"], -150)
                self.assertEqual(account["balance"], -50)
                self.assertEqual(account["ending_balance"], -150 + -50)

    def test02_trial_analytic_balance_with_splited_accounts(self):
        res_data = self._get_report_lines(account_ids=[self.aaa_1.id, self.aaa_2.id])
        trial_analytic_balance = res_data["trial_balance"]
        totals = res_data["total_amounts"]

        accounts_in_report = self._accounts_in_report(trial_analytic_balance)
        self.assertTrue(len(accounts_in_report) == 2)
        self.assertTrue(self.expense_account.id in accounts_in_report)
        self.assertTrue(self.income_account.id in accounts_in_report)
        self.assertFalse(self.income_account_2.id in accounts_in_report)

        key1 = f"{self.aaa_1.code if self.aaa_1.code else ''} {self.aaa_1.name}".strip()
        key2 = f"{self.aaa_2.code if self.aaa_2.code else ''} {self.aaa_2.name}".strip()

        self.assertTrue(key1 in res_data["account_code_list"])
        self.assertTrue(key2 in res_data["account_code_list"])

        # Checks total amounts by account type
        self._check_total_amounts_by_acc_type(
            res_data["totals_by_acc_type"], include_both_accounts=True
        )

        # Checks total amounts
        self.assertEqual(totals["total_initial_balance"], -150)
        self.assertEqual(
            totals["total_ending_balance"],
            -150 + -50 + 250,
        )

        for aaa_id, amount in totals["total_period_balance"].items():
            if aaa_id == self.aaa_2.id:
                self.assertEqual(amount, -50 + 250)
            else:
                self.assertEqual(amount, 0)

        # Check balances for every account
        for account in trial_analytic_balance:
            if account["id"] == self.income_account.id:
                self.assertEqual(account["initial_balance"], 0)
                self.assertEqual(account["ending_balance"], 250)
                for aaa_id, amount in account["accounts"].items():
                    if aaa_id == self.aaa_2.id:
                        self.assertEqual(amount, 250)
                    else:
                        self.assertEqual(amount, 0)
            else:
                self.assertEqual(account["initial_balance"], -150)
                self.assertEqual(account["ending_balance"], -150 + -50)
                for aaa_id, amount in account["accounts"].items():
                    if aaa_id == self.aaa_2.id:
                        self.assertEqual(amount, -50)
                    else:
                        self.assertEqual(amount, 0)

    def test03_trial_analytic_balance_gruped_by_analytic_account(self):
        res_data = self._get_report_lines(group_by_analytic_account=True)
        trial_analytic_balance = res_data["trial_balance"]
        totals = res_data["total_amounts"]
        accounts_in_report = self._accounts_in_report(trial_analytic_balance)

        self.assertTrue(len(accounts_in_report) == 2)
        self.assertTrue(self.aaa_1.id in accounts_in_report)
        self.assertTrue(self.aaa_2.id in accounts_in_report)

        self._check_total_amounts_by_acc_type(res_data["totals_by_acc_type"])
        self.assertEqual(totals["total_initial_balance"], -150)
        self.assertEqual(totals["total_period_balance"], -50 + 250)
        self.assertEqual(
            totals["total_ending_balance"],
            -150 + -50 + 250,
        )

        for account in trial_analytic_balance:
            if account["id"] == self.aaa_1.id:
                self.assertEqual(account["initial_balance"], -150)
                self.assertEqual(account["balance"], 0)
                self.assertEqual(account["ending_balance"], -150)
            else:
                self.assertEqual(account["initial_balance"], 0)
                self.assertEqual(account["balance"], -50 + 250)
                self.assertEqual(account["ending_balance"], -50 + 250)

    def test04_trial_analytic_balance_gruped_by_analytic_account_filtered(self):
        res_data = self._get_report_lines(
            group_by_analytic_account=True, account_ids=[self.aaa_1.id]
        )
        trial_analytic_balance = res_data["trial_balance"]
        totals = res_data["total_amounts"]
        accounts_in_report = self._accounts_in_report(trial_analytic_balance)

        self.assertTrue(len(accounts_in_report) == 1)
        self.assertTrue(self.aaa_1.id in accounts_in_report)
        self.assertFalse(self.aaa_2.id in accounts_in_report)

        for type_name, total_by_acc_type in res_data["totals_by_acc_type"].items():
            if type_name == self.account_type_map["expense"]:
                self.assertEqual(total_by_acc_type["total_initial_balance"], -150)
                self.assertEqual(total_by_acc_type["total_period_balance"], 0)
                self.assertEqual(total_by_acc_type["total_ending_balance"], -150)
        self.assertEqual(totals["total_initial_balance"], -150)
        self.assertEqual(totals["total_period_balance"], 0)
        self.assertEqual(totals["total_ending_balance"], -150)

        for account in trial_analytic_balance:
            if account["id"] == self.aaa_1.id:
                self.assertEqual(account["initial_balance"], -150)
                self.assertEqual(account["balance"], 0)
                self.assertEqual(account["ending_balance"], -150)

    def test05_trial_analytic_balance_show_hirarchy(self):
        self.env["account.analytic.line"].create(
            {
                "name": "aal 1",
                self.account_field: self.aaa_2.id,
                "general_account_id": self.income_account_2.id,
                "amount": 300,
                "date": "2024-12-31",
            }
        )
        res_data = self._get_report_lines(show_hierarchy=True)
        trial_analytic_balance = res_data["trial_balance"]
        accounts_in_report = self._accounts_in_report(trial_analytic_balance)
        totals = res_data["total_amounts"]

        self.assertTrue(len(accounts_in_report) == 6)
        self.assertTrue(self.expense_account.id in accounts_in_report)
        self.assertTrue(self.income_account.id in accounts_in_report)
        self.assertTrue(self.income_account_2.id in accounts_in_report)

        # Checks total amounts by account type
        for type_name, total_by_acc_type in res_data["totals_by_acc_type"].items():
            if type_name == self.account_type_map["expense"]:
                self.assertTrue(total_by_acc_type["total_initial_balance"] == -150)
                self.assertTrue(total_by_acc_type["total_period_balance"] == -50)
                self.assertTrue(total_by_acc_type["total_ending_balance"] == -200)
            elif type_name == self.account_type_map["income"]:
                self.assertTrue(total_by_acc_type["total_initial_balance"] == 0)
                self.assertTrue(total_by_acc_type["total_period_balance"] == 250 + 300)
                self.assertTrue(total_by_acc_type["total_ending_balance"] == 250 + 300)

        # Checks total amounts
        self.assertEqual(totals["total_initial_balance"], -150)
        self.assertEqual(totals["total_period_balance"], -50 + 250 + 300)
        self.assertEqual(totals["total_ending_balance"], -150 + -50 + 250 + 300)

        # Check balances for every account
        for account in trial_analytic_balance:
            if account["type"] == "group_type":
                if account["code"] == "4":
                    self.assertEqual(account["name"], "Group 4")
                    self.assertEqual(account["complete_code"], "4")
                    self.assertEqual(account["level"], 0)
                    self.assertTrue(self.income_account.id in account["account_ids"])
                    self.assertEqual(account["initial_balance"], 0)
                    self.assertEqual(account["balance"], 250 + 300)
                    self.assertEqual(account["ending_balance"], 250 + 300)
                if account["code"] == "42":
                    self.assertEqual(account["name"], "Group 4")
                    self.assertEqual(account["complete_code"], "4/42")
                    self.assertEqual(account["level"], 1)
                    self.assertTrue(self.income_account_2.id in account["account_ids"])
                    self.assertEqual(account["initial_balance"], 0)
                    self.assertEqual(account["balance"], 300)
                    self.assertEqual(account["ending_balance"], 300)
                if account["code"] == "5":
                    self.assertEqual(account["name"], "Group 5")
                    self.assertEqual(account["complete_code"], "5")
                    self.assertEqual(account["level"], 0)
                    self.assertTrue(self.expense_account.id in account["account_ids"])
                    self.assertEqual(account["initial_balance"], -150)
                    self.assertEqual(account["balance"], -50)
                    self.assertEqual(account["ending_balance"], -150 + -50)
            else:
                if account["id"] == self.income_account.id:
                    self.assertEqual(account["initial_balance"], 0)
                    self.assertEqual(account["balance"], 250)
                    self.assertEqual(account["ending_balance"], 250)
                elif account["id"] == self.income_account_2.id:
                    self.assertEqual(account["initial_balance"], 0)
                    self.assertEqual(account["balance"], 300)
                    self.assertEqual(account["ending_balance"], 300)
                else:
                    self.assertEqual(account["initial_balance"], -150)
                    self.assertEqual(account["balance"], -50)
                    self.assertEqual(account["ending_balance"], -150 + -50)

    def test06_trial_analytic_balance_filtered_by_financial_accounts(self):
        res_data = self._get_report_lines(
            financial_account_ids=[self.expense_account.id]
        )
        trial_analytic_balance = res_data["trial_balance"]
        accounts_in_report = self._accounts_in_report(trial_analytic_balance)
        totals = res_data["total_amounts"]

        self.assertTrue(len(accounts_in_report) == 1)
        self.assertTrue(self.expense_account.id in accounts_in_report)
        self.assertFalse(self.income_account.id in accounts_in_report)
        self.assertFalse(self.income_account_2.id in accounts_in_report)

        # Checks total amounts by account type
        self.assertEqual(len(res_data["totals_by_acc_type"]), 1)
        for __type_name, total_by_acc_type in res_data["totals_by_acc_type"].items():
            self.assertTrue(total_by_acc_type["total_initial_balance"] == -150)
            self.assertTrue(total_by_acc_type["total_period_balance"] == -50)
            self.assertTrue(total_by_acc_type["total_ending_balance"] == -200)

        # Checks total amounts
        self.assertEqual(totals["total_initial_balance"], -150)
        self.assertEqual(totals["total_period_balance"], -50)
        self.assertEqual(
            totals["total_ending_balance"],
            -150 + -50,
        )

        # Check balances for every account
        for account in trial_analytic_balance:
            self.assertEqual(account["initial_balance"], -150)
            self.assertEqual(account["balance"], -50)
            self.assertEqual(account["ending_balance"], -150 + -50)

    def test07_trial_analytic_balance_by_financial_accounts_and_analytic_account(self):
        res_data = self._get_report_lines(
            account_ids=[self.aaa_1.id],
            financial_account_ids=[self.expense_account.id],
        )
        trial_analytic_balance = res_data["trial_balance"]
        accounts_in_report = self._accounts_in_report(trial_analytic_balance)
        totals = res_data["total_amounts"]

        self.assertTrue(len(accounts_in_report) == 1)
        self.assertTrue(self.expense_account.id in accounts_in_report)
        self.assertFalse(self.income_account.id in accounts_in_report)
        self.assertFalse(self.income_account_2.id in accounts_in_report)

        # Checks total amounts by account type
        self.assertEqual(len(res_data["totals_by_acc_type"]), 1)
        for __type_name, total_by_acc_type in res_data["totals_by_acc_type"].items():
            self.assertTrue(total_by_acc_type["total_initial_balance"] == -150)
            self.assertTrue(
                total_by_acc_type["total_period_balance"][self.aaa_1.id] == 0.0
            )
            self.assertTrue(total_by_acc_type["total_ending_balance"] == -150)

        # Checks total amounts
        self.assertEqual(totals["total_initial_balance"], -150)
        self.assertEqual(totals["total_period_balance"][self.aaa_1.id], 0.0)
        self.assertEqual(totals["total_ending_balance"], -150)

        # Check balances for every account
        for account in trial_analytic_balance:
            self.assertEqual(account["initial_balance"], -150)
            self.assertEqual(account["accounts"][self.aaa_1.id], 0.0)
            self.assertEqual(account["ending_balance"], -150)
