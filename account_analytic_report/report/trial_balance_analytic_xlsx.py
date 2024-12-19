# Copyright 2024 (APSL - Nagarro) Bernat Obrador
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import datetime

from dateutil.relativedelta import relativedelta

from odoo import _, models


class TrialBalanceXslx(models.AbstractModel):
    _name = "report.a_a_r.report_trial_balance_analytic_xlsx"
    _description = "Trial Balance XLSX Report"
    _inherit = "report.account_analytic_report.abstract_report_xlsx"

    def _get_report_name(self, report, data=False):
        company_id = data.get("company_id", False)
        account_code = data.get("account_code", False)
        report_name = _("Analytic Trial Balance")
        if company_id:
            company = self.env["res.company"].browse(company_id)
            suffix = f" - {company.name} - {company.currency_id.name}"
            report_name = report_name + suffix
        if account_code:
            report_name += f" [{account_code}]"
        return report_name

    def _is_report_with_include_both_accounts(self, report):
        return report.account_ids and not report.group_by_analytic_account

    def _get_report_columns(self, report):
        if self._is_report_with_include_both_accounts(report):
            codes = self.env["account.analytic.account"].search(
                [("id", "in", report.account_ids.ids)]
            )
            res = {
                0: {"header": _("Code"), "field": "code", "width": 15},
                1: {"header": _("Account"), "field": "name", "width": 70},
                2: {
                    "header": _("Initial balance"),
                    "field": "initial_balance",
                    "type": "amount",
                    "width": 14,
                },
            }
            for i, account in enumerate(codes):
                res[i + 3] = {
                    "header": f"{account.code if account.code else ''} {account.name}",
                    "id": account.id,
                    "field": "accounts",
                    "type": "amount",
                    "width": 14,
                }

            res[len(res)] = {
                "header": _("Ending balance"),
                "field": "ending_balance",
                "type": "amount",
                "width": 14,
            }
        else:
            res = {
                0: {"header": _("Code"), "field": "code", "width": 10},
                1: {"header": _("Account"), "field": "name", "width": 70},
                2: {
                    "header": _("Initial balance"),
                    "field": "initial_balance",
                    "type": "amount",
                    "width": 14,
                },
                3: {
                    "header": _("Period balance"),
                    "field": "balance",
                    "type": "amount",
                    "width": 14,
                },
                4: {
                    "header": _("Ending balance"),
                    "field": "ending_balance",
                    "type": "amount",
                    "width": 14,
                },
            }
        return res

    def _get_report_filters(self, report):
        report_filters = [
            [
                _("Date range filter"),
                _("From: %(date_from)s To: %(date_to)s")
                % ({"date_from": report.date_from, "date_to": report.date_to}),
            ],
            [_("Selected Plan"), report.plan_id.name],
            [
                _("Grouped by analytic account"),
                _("Yes") if report.group_by_analytic_account else _("No"),
            ],
        ]

        if report.account_ids:
            account_codes = self.env[
                "report.account_analytic_report.trial_balance_analytic"
            ]._get_account_codes(report.account_ids.ids)
            report_filters.append(
                [
                    _("Accounts Filter"),
                    account_codes,
                ]
            )

        report_filters.append(
            [
                _("Limit hierarchy levels"),
                (
                    _("Level %s") % (report.hierarchy_level)
                    if report.limit_hierarchy_level
                    else _("No limit")
                ),
            ]
        )

        return report_filters

    def _get_col_count_filter_name(self):
        return 2

    def _get_col_count_filter_value(self):
        return 3

    def _write_trial_analytic(self, report_values, report_data):
        for balance in report_values["trial_balance"]:
            if (
                report_values["show_hierarchy"]
                and report_values["limit_hierarchy_level"]
            ):
                if report_values["hierarchy_level"] > balance["level"]:
                    self.write_line_from_dict(balance, report_data)
            else:
                self.write_line_from_dict(balance, report_data)

    def _generate_report_content(self, workbook, report, data, report_data):
        report_values = self._get_values_from_report(report, data)
        report_data["account_code_list"] = report_values["account_code_list"]
        report_data["group_by_analytic_account"] = report_values[
            "group_by_analytic_account"
        ]
        report_data["total_amounts"] = report_values["total_amounts"]
        self.write_array_header(report_data)

        self._write_trial_analytic(report_values, report_data)

        total_rows_by_account_type = self._prepare_total_rows_by_account_type(
            report_values, report
        )

        for row in total_rows_by_account_type:
            self._write_line_with_format(
                report_data,
                row,
                report_data["formats"]["format_acc_type_total"],
                report_data["formats"]["format_acc_type_amount_total"],
            )

        total_row = self._prepare_total_row(report_values, report)
        self._write_line_with_format(
            report_data,
            total_row,
            report_data["formats"]["format_total"],
            report_data["formats"]["format_amount_total"],
        )

        if report_values["show_months"]:
            self.create_page_by_anlytic_accounts(
                workbook, report, report_data, report_values
            )

    def _prepare_total_row(self, report_values, report):
        total_row = {
            "name": _("Total"),
            "initial_balance": report_values["total_amounts"]["total_initial_balance"],
            "ending_balance": report_values["total_amounts"]["total_ending_balance"],
        }
        total_period_balance = report_values["total_amounts"]["total_period_balance"]
        if self._is_report_with_include_both_accounts(report):
            total_row["accounts"] = {}
            codes = self.env["account.analytic.account"].search(
                [("id", "in", report.account_ids.ids)]
            )
            for account in codes:
                total_row["accounts"][account.id] = total_period_balance.get(
                    account.id, 0
                )
        else:
            total_row["balance"] = total_period_balance

        return total_row

    def _prepare_total_rows_by_account_type(self, report_values, report):
        total_rows = []
        for acc_type, balances in report_values["totals_by_acc_type"].items():
            total_row = {
                "name": acc_type,
                "initial_balance": balances["total_initial_balance"],
                "ending_balance": balances["total_ending_balance"],
            }
            if self._is_report_with_include_both_accounts(report):
                total_row["accounts"] = {}
                codes = self.env["account.analytic.account"].search(
                    [("id", "in", report.account_ids.ids)]
                )
                for account in codes:
                    if account.id in balances["total_period_balance"].keys():
                        total_row["accounts"].update(
                            {account.id: balances["total_period_balance"][account.id]}
                        )
            else:
                total_row["balance"] = balances["total_period_balance"]
            total_rows.append(total_row)
        return total_rows

    def _get_values_from_report(self, report, data):
        res_data = self.env[
            "report.account_analytic_report.trial_balance_analytic"
        ]._get_report_values(report, data)
        return {
            "show_hierarchy": res_data["show_hierarchy"],
            "hierarchy_level": res_data["show_hierarchy_level"],
            "limit_hierarchy_level": res_data["limit_hierarchy_level"],
            "account_code_list": res_data["account_code_list"],
            "show_months": res_data["show_months"],
            "group_by_analytic_account": res_data["group_by_analytic_account"],
            "trial_balance": res_data["trial_balance"],
            "plan_field": res_data["plan_field"],
            "total_amounts": res_data["total_amounts"],
            "totals_by_acc_type": res_data["totals_by_acc_type"],
            "account_ids": res_data["account_ids"],
            "financial_account_ids": res_data["financial_account_ids"],
        }

    def _write_line_with_format(self, report_data, row, str_format, amount_format):
        for col_pos, column in report_data["columns"].items():
            value = row.get(column["field"], False)
            cell_type = column.get("type", "string")

            if cell_type == "amount":
                value = value if value else 0
                cell_format = amount_format

                if column["field"] == "accounts":
                    value = value[column["id"]]
                report_data["sheet"].write_number(
                    report_data["row_pos"], col_pos, float(value), cell_format
                )
            elif cell_type == "string":
                value = value if value else ""
                report_data["sheet"].write_string(
                    report_data["row_pos"], col_pos, str(value), str_format
                )
        report_data["row_pos"] += 1

    def _prepare_data_for_page(self, report):
        date_from = report.date_from.strftime("%Y-%m-%d")
        date_to = report.date_to.strftime("%Y-%m-%d")
        account_id_field = report.plan_id._column_name()
        company_id = report.company_id.id
        filters = self._get_report_filters(report)

        return {
            "date_from": date_from,
            "date_to": date_to,
            "account_id_field": account_id_field,
            "company_id": company_id,
            "filters": filters,
        }

    def _create_page_for_account(
        self,
        workbook,
        company_id,
        report_data,
        account,
        filters,
        date_from,
        date_to,
        report_values,
    ):
        """
        Adds a new worksheet for each account using its code as the sheet name.
        """
        account_key = f"{account.code if account.code else ''} {account.name}"
        sheet = workbook.add_worksheet(account_key)
        report_data["sheet"] = sheet
        report_data["row_pos"] = 0
        filters[4][1] = account_key

        self._write_report_title(
            self._get_report_name(
                report_data, {"company_id": company_id, "account_code": account_key}
            ),
            report_data,
        )
        self._write_filters(filters, report_data)

        return sheet

    def _get_report_columns_by_month(self, date_from, date_to, account):
        res = {
            0: {"header": _("Code"), "field": "code", "width": 15},
            1: {"header": _("Account"), "field": "name", "width": 50},
        }

        date_from = datetime.strptime(date_from, "%Y-%m-%d")
        date_to = datetime.strptime(date_to, "%Y-%m-%d")

        current_date = date_from

        # Loop through each month between date_from and date_to
        while current_date <= date_to:
            month_year = current_date.strftime("%m-%Y")

            # Add a new column for this month
            res[len(res)] = {
                "header": month_year,
                "field": f"{current_date.month}-{current_date.year}",
                "type": "amount",
                "width": 14,
            }

            # Move to the next month
            current_date += relativedelta(months=1)

        res[len(res)] = {
            "header": _("Total"),
            "field": "total",
            "type": "amount",
            "width": 14,
        }
        return res

    def _get_months_query(
        self, company_id, account_id_field, account, date_from, date_to, report_values
    ):
        ids = report_values.get("financial_account_ids") or []
        filter_accounts = ""
        if ids:
            ids_tuple = tuple(ids)
            filter_accounts = f"AND aal.general_account_id IN {ids_tuple}"

        query = f"""
            SELECT
                aal.general_account_id,
                date_trunc('month', aal.date::timestamp)::date AS month,
                COUNT(*) AS n,
                SUM(aal.amount) AS amt
            FROM account_analytic_line AS aal
            LEFT JOIN account_account AS acc
                ON acc.id = aal.general_account_id
            LEFT JOIN res_company AS rc
                ON rc.id = acc.company_id
            WHERE
                aal.{account_id_field} = {account.id}
                AND aal.company_id = {company_id}
                AND aal.date >= '{date_from}'
                AND aal.date <= '{date_to}'
                {filter_accounts}
            GROUP BY
                aal.general_account_id, month, acc.code, rc.sequence, rc.name
            ORDER BY
                acc.code, rc.sequence, rc.name, month ASC;
        """
        return query

    def _get_total_acc_type_by_month_query(
        self,
        company_id,
        account_id_field,
        account,
        date_from,
        date_to,
        financial_account_ids=None,
    ):
        filter_accounts = ""
        if financial_account_ids:
            ids_tuple = tuple(financial_account_ids)
            filter_accounts = f"AND aal.general_account_id IN {ids_tuple}"
        return f"""
        SELECT
            aa.account_type,
            aal.{account_id_field},
            date_trunc('month', aal.date::timestamp)::date AS month,
            SUM(amount) AS total_amount
        FROM
            account_analytic_line AS aal
        INNER JOIN
            account_account AS aa ON aa.id = aal.general_account_id
        WHERE
            aal.company_id = {company_id}
            AND aal.{account_id_field} IS NOT NULL
            AND aal.date >= '{date_from}'
            AND aal.date <= '{date_to}'
            AND aal.{account_id_field} = {account.id}
            {filter_accounts}
        GROUP BY
            aa.account_type,
            aal.{account_id_field},
            date_trunc('month', aal.date::timestamp)::date
        ORDER BY
            month ASC;
        """

    def _get_total_acc_type_by_month(
        self,
        company_id,
        account_id_field,
        account,
        date_from,
        date_to,
        financial_account_ids=None,
    ):
        self.env.cr.execute(
            self._get_total_acc_type_by_month_query(
                company_id,
                account_id_field,
                account,
                date_from,
                date_to,
                financial_account_ids=financial_account_ids,
            )
        )
        total_acc_type_by_months = self.env.cr.fetchall()

        # Maps the accounts with his redebale name
        account_type_mapping = self.env[
            "report.account_analytic_report.trial_balance_analytic"
        ]._get_account_type_mapping()

        for i, acc_type in enumerate(total_acc_type_by_months):
            total_acc_type_by_months[i] = (
                account_type_mapping[acc_type[0]],
                *acc_type[1:],
            )

        return total_acc_type_by_months

    def _get_total_acc_type_by_months_rows(self, total_acc_type_by_months):
        total_acc_type_by_months_rows = {}
        for total_acc_type in total_acc_type_by_months:
            account_type_name = total_acc_type[0]
            month_year = f"{total_acc_type[2].month}-{total_acc_type[2].year}"
            amount = total_acc_type[3]

            if account_type_name not in total_acc_type_by_months_rows:
                total_acc_type_by_months_rows[account_type_name] = {
                    "name": account_type_name,
                    "total": 0,
                }

            total_acc_type_by_months_rows[account_type_name][month_year] = amount
            total_acc_type_by_months_rows[account_type_name]["total"] += amount

        return total_acc_type_by_months_rows

    def _get_amounts_and_total_by_analytic_account(self, amounts_data_by_month):
        amounts_by_month = {}
        total_row = {"code": _("Total"), "total": 0}
        for amount_data in amounts_data_by_month:
            account_account = self.env["account.account"].browse(amount_data[0])
            key = f"{amount_data[1].month}-{amount_data[1].year}"
            amount = amount_data[3]

            total_row[key] = total_row.get(key, 0) + amount
            total_row["total"] += amount

            if account_account.id not in amounts_by_month:
                amounts_by_month[account_account.id] = {
                    "code": account_account.code,
                    "name": account_account.name,
                    "total": 0,
                }

            amounts_by_month[account_account.id][key] = amount
            amounts_by_month[account_account.id]["total"] += amount
        return amounts_by_month, total_row

    def _write_amount_by_month(self, amounts_by_month, report_data):
        for amount_by_month in amounts_by_month.values():
            if isinstance(amount_by_month, dict):
                self.write_line_from_dict(amount_by_month, report_data)

    def _write_totals_by_acc_type(self, total_acc_type_by_months, report_data):
        total_acc_type_month_row = self._get_total_acc_type_by_months_rows(
            total_acc_type_by_months
        )
        # Writes total by account type
        for row in total_acc_type_month_row.values():
            self._write_line_with_format(
                report_data,
                row,
                report_data["formats"]["format_acc_type_total"],
                report_data["formats"]["format_acc_type_amount_total"],
            )

    def _write_total_row(self, total_row, report_data):
        # Writes total row
        self._write_line_with_format(
            report_data,
            total_row,
            report_data["formats"]["format_total"],
            report_data["formats"]["format_amount_total"],
        )

    def create_page_by_anlytic_accounts(
        self, workbook, report, report_data, report_values
    ):
        report_data_values = self._prepare_data_for_page(report)
        date_from = report_data_values["date_from"]
        date_to = report_data_values["date_to"]
        account_id_field = report_data_values["account_id_field"]
        filters = report_data_values["filters"]
        company_id = report_data_values["company_id"]
        for account in report.account_ids:
            self._create_page_for_account(
                workbook,
                company_id,
                report_data,
                account,
                filters,
                date_from,
                date_to,
                report_values,
            )

            query = self._get_months_query(
                company_id, account_id_field, account, date_from, date_to, report_values
            )

            self.env.cr.execute(query)

            amounts_data_by_month = self.env.cr.fetchall()

            report_data["columns"] = self._get_report_columns_by_month(
                date_from, date_to, account
            )

            self.write_array_header(report_data)
            self._set_column_width(report_data)

            (
                amounts_by_month,
                total_row,
            ) = self._get_amounts_and_total_by_analytic_account(amounts_data_by_month)
            amounts_by_month.update({"account_id": account.id})
            self._write_amount_by_month(amounts_by_month, report_data)

            total_acc_type_by_months = self._get_total_acc_type_by_month(
                company_id,
                account_id_field,
                account,
                date_from,
                date_to,
                financial_account_ids=report_values["financial_account_ids"],
            )

            self._write_totals_by_acc_type(total_acc_type_by_months, report_data)

            self._write_total_row(total_row, report_data)
