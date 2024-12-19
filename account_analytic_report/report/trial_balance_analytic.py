# Copyright 2024 (APSL - Nagarro) Bernat Obrador
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo import api, models
from odoo.tools.float_utils import float_is_zero


class TrialBalanceAnalyticReport(models.AbstractModel):
    _name = "report.account_analytic_report.trial_balance_analytic"
    _description = "Trial Balance Analytic Report"

    def _get_accounts_data(self, accounts_ids, group_by_field):
        if group_by_field == "general_account_id":
            accounts = self.env["account.account"].search([("id", "in", accounts_ids)])
        else:
            accounts = self.env["account.analytic.account"].search(
                [("id", "in", accounts_ids)]
            )
        accounts_data = {}
        for account in accounts:
            accounts_data.update(
                {
                    account.id: {
                        "id": account.id,
                        "name": account.name,
                        "code": account.code or account.name,
                    }
                }
            )
        return accounts_data

    def _get_base_domain(
        self,
        account_ids,
        company_id,
        account_id_field,
        plan_id,
        group_by_field,
        financial_account_ids=None,
    ):
        accounts_domain = [
            ("company_id", "=", company_id),
            ("root_plan_id", "=", plan_id),
        ]
        if account_ids:
            accounts_domain += [("id", "in", account_ids)]

        accounts = self.env["account.analytic.account"].search(accounts_domain)

        domain = [
            (account_id_field, "in", accounts.ids),
            (account_id_field, "!=", False),
            (group_by_field, "!=", False),
        ]
        if company_id:
            domain += [("company_id", "=", company_id)]
        if financial_account_ids:
            domain += [("general_account_id", "in", financial_account_ids)]
        return domain

    def _get_initial_balances_bs_ml_domain(self, domain, date_from, fy_start_date):
        bs_ml_domain = domain + [
            ("date", "<", date_from),
            ("date", ">=", fy_start_date),
        ]
        return bs_ml_domain

    @api.model
    def _get_period_ml_domain(
        self,
        domain,
        date_to,
        date_from,
    ):
        ml_domain = domain + [
            ("date", ">=", date_from),
            ("date", "<=", date_to),
        ]
        return ml_domain

    @api.model
    def _compute_account_amount(
        self,
        total_amount,
        tb_initial_acc,
        tb_period_acc,
        group_by_field,
        account_id_field=None,
        account_ids=None,
    ):
        """
        Prepares the total amount dict with inital balance, period balance and
        ending balance.
        If account_ids is not null and we are not grouping by analytic account,
        it will split the ammount in the analytic account and financial account
        """
        for tb in tb_period_acc:
            if tb[group_by_field]:
                self._prepare_amounts(
                    tb, group_by_field, total_amount, account_id_field, account_ids
                )
        for tb in tb_initial_acc:
            id_field = group_by_field if account_ids else "account_id"
            acc_id = tb[id_field]
            if acc_id not in total_amount.keys():
                total_amount[acc_id] = self._prepare_total_amount(tb, account_ids)
            else:
                total_amount[acc_id]["initial_balance"] = tb["amount"]
                total_amount[acc_id]["ending_balance"] += tb["amount"]
        return total_amount

    def _prepare_amounts(
        self, tb, group_by_field, total_amount, account_id_field, account_ids=None
    ):
        if account_ids:
            acc_id = tb[group_by_field][0]
            if acc_id not in total_amount.keys():
                total_amount[acc_id] = self._prepare_total_amount(tb, account_ids)
                total_amount[acc_id][tb[account_id_field][0]] = tb["amount"]
                total_amount[acc_id]["initial_balance"] = 0.0
            else:
                total_amount[acc_id][tb[account_id_field][0]] = tb["amount"]
                total_amount[acc_id]["ending_balance"] += tb["amount"]
                total_amount[acc_id]["initial_balance"] = 0.0
        else:
            acc_id = tb[group_by_field][0]
            total_amount[acc_id] = self._prepare_total_amount(tb)
            total_amount[acc_id]["amount"] = tb["amount"]
            total_amount[acc_id]["initial_balance"] = 0.0

    @api.model
    def _prepare_total_amount(self, tb, account_ids=None):
        res = {
            "amount": 0.0,
            "initial_balance": tb["amount"],
            "ending_balance": tb["amount"],
        }
        if account_ids:
            for account in account_ids:
                res[account] = 0.0

        return res

    def _remove_accounts_at_cero(self, total_amount, company):
        def is_removable(d):
            rounding = company.currency_id.rounding
            return float_is_zero(
                d["initial_balance"], precision_rounding=rounding
            ) and float_is_zero(d["ending_balance"], precision_rounding=rounding)

        accounts_to_remove = []
        for acc_id, ta_data in total_amount.items():
            if is_removable(ta_data):
                accounts_to_remove.append(acc_id)
        for account_id in accounts_to_remove:
            del total_amount[account_id]

    def _get_hierarchy_groups(self, group_ids, groups_data):
        for group_id in group_ids:
            parent_id = groups_data[group_id]["parent_id"]
            while parent_id:
                if parent_id not in groups_data.keys():
                    group = self.env["account.group"].browse(parent_id)
                    groups_data[group.id] = {
                        "id": group.id,
                        "code": group.code_prefix_start,
                        "name": group.name,
                        "parent_id": group.parent_id.id,
                        "parent_path": group.parent_path,
                        "complete_code": group.complete_code,
                        "account_ids": group.compute_account_ids.ids,
                        "type": "group_type",
                        "initial_balance": 0,
                        "balance": 0,
                        "ending_balance": 0,
                    }
                acc_keys = ["balance"]
                acc_keys += ["initial_balance", "ending_balance"]
                for acc_key in acc_keys:
                    groups_data[parent_id][acc_key] += groups_data[group_id][acc_key]
                parent_id = groups_data[parent_id]["parent_id"]
        return groups_data

    def _get_groups_data(self, accounts_data, total_amount):
        accounts_ids = list(accounts_data.keys())
        accounts = self.env["account.account"].browse(accounts_ids)
        account_group_relation = {}
        for account in accounts:
            accounts_data[account.id]["complete_code"] = (
                account.group_id.complete_code + " / " + account.code
                if account.group_id.id
                else ""
            )
            if account.group_id.id:
                if account.group_id.id not in account_group_relation.keys():
                    account_group_relation.update({account.group_id.id: [account.id]})
                else:
                    account_group_relation[account.group_id.id].append(account.id)
        groups = self.env["account.group"].browse(account_group_relation.keys())
        groups_data = {}
        for group in groups:
            groups_data.update(
                {
                    group.id: {
                        "id": group.id,
                        "code": group.code_prefix_start,
                        "name": group.name,
                        "parent_id": group.parent_id.id,
                        "parent_path": group.parent_path,
                        "type": "group_type",
                        "complete_code": group.complete_code,
                        "account_ids": group.compute_account_ids.ids,
                        "initial_balance": 0.0,
                        "balance": 0.0,
                        "ending_balance": 0.0,
                    }
                }
            )
        for group_id in account_group_relation.keys():
            for account_id in account_group_relation[group_id]:
                groups_data[group_id]["initial_balance"] += total_amount[account_id][
                    "initial_balance"
                ]
                groups_data[group_id]["balance"] += total_amount[account_id]["amount"]
                groups_data[group_id]["ending_balance"] += total_amount[account_id][
                    "ending_balance"
                ]
        group_ids = list(groups_data.keys())
        groups_data = self._get_hierarchy_groups(
            group_ids,
            groups_data,
        )
        return groups_data

    def _hide_accounts_at_0(self, company_id, total_amount):
        company = self.env["res.company"].browse(company_id)
        self._remove_accounts_at_cero(total_amount, company)

    def _get_tb_initial_acc_bs(
        self, domain, date_from, fy_start_date, fields, group_by, lazy=True
    ):
        initial_domain_bs = self._get_initial_balances_bs_ml_domain(
            domain,
            date_from,
            fy_start_date,
        )
        return self.env["account.analytic.line"].read_group(
            domain=initial_domain_bs,
            fields=fields,
            groupby=group_by,
            lazy=lazy,
        )

    def _get_tb_period_acc(
        self, domain, date_to, date_from, fields, group_by, lazy=True
    ):
        period_domain = self._get_period_ml_domain(
            domain,
            date_to,
            date_from,
        )
        return self.env["account.analytic.line"].read_group(
            domain=period_domain, fields=fields, groupby=group_by, lazy=lazy
        )

    def _get_account_codes(self, account_ids):
        analytic_accounts = self.env["account.analytic.account"].search(
            [("id", "in", account_ids)]
        )
        account_codes = [
            f"{account.code if account.code else ''} {account.name}"
            for account in sorted(analytic_accounts, key=lambda account: account.id)
        ]
        codes_string = ", ".join(account_codes)
        return codes_string

    def _clean_account_codes(self, account_codes):
        return (
            [code.strip() for code in account_codes.split(",")]
            if account_codes
            else None
        )

    def _update_accounts_data(
        self,
        accounts_data,
        total_amount,
        total_amounts,
        include_both_accounts=False,
        account_ids=None,
    ):
        for account_id in accounts_data.keys():
            accounts_data[account_id].update(
                {
                    "initial_balance": total_amount[account_id]["initial_balance"],
                    "ending_balance": total_amount[account_id]["ending_balance"],
                    "type": "account_type",
                    "code": accounts_data[account_id]["code"],
                }
            )
            total_amounts["total_initial_balance"] += total_amount[account_id][
                "initial_balance"
            ]
            total_amounts["total_ending_balance"] += total_amount[account_id][
                "ending_balance"
            ]
            # If the report requires both account details, add a nested
            # structure within each account. So now we can have the amount
            # by the analytic account and the financial account
            if include_both_accounts:
                accounts_data[account_id]["accounts"] = {}
                for account in account_ids:
                    accounts_data[account_id]["accounts"][account] = total_amount[
                        account_id
                    ][account]
                    if account not in total_amounts["total_period_balance"]:
                        total_amounts["total_period_balance"][account] = 0
                    total_amounts["total_period_balance"][account] += total_amount[
                        account_id
                    ][account]
            else:
                accounts_data[account_id].update(
                    {"balance": total_amount[account_id]["amount"]}
                )
                total_amounts["total_period_balance"] += total_amount[account_id][
                    "amount"
                ]

    def _get_trial_balance(self, accounts_data, total_amount, show_hierarchy):
        if show_hierarchy:
            groups_data = self._get_groups_data(accounts_data, total_amount)
            trial_balance = list(groups_data.values()) + list(accounts_data.values())
            trial_balance = sorted(trial_balance, key=lambda k: k["complete_code"])
            for trial in trial_balance:
                trial["level"] = trial["complete_code"].count("/")
        else:
            trial_balance = list(accounts_data.values())
        return trial_balance

    def _get_total_amounts_dict(self, include_both_accounts):
        return {
            "total_initial_balance": 0,
            "total_period_balance": {} if include_both_accounts else 0,
            "total_ending_balance": 0,
        }

    def _get_archived_account_ids(self, company_id):
        return (
            self.env["account.analytic.account"]
            .search([("company_id", "=", company_id), ("active", "=", False)])
            .ids
        )

    @api.model
    def _get_data_splited_by_accounts(
        self,
        account_ids,
        company_id,
        date_to,
        date_from,
        fy_start_date,
        plan_field,
        plan_id,
        financial_account_ids=None,
    ):
        """
        This function gives the report grouped by financial account and
        analytic account spliting the ammount by the 2 accounts
        """
        domain = self._get_base_domain(
            account_ids,
            company_id,
            plan_field,
            plan_id,
            "general_account_id",
            financial_account_ids=financial_account_ids,
        )
        tb_initial_acc_bs = self._get_tb_initial_acc_bs(
            domain=domain,
            date_from=date_from,
            fy_start_date=fy_start_date,
            fields=[plan_field, "general_account_id", "amount"],
            group_by=["general_account_id", plan_field],
            lazy=False,
        )
        tb_initial_acc = []
        for line in tb_initial_acc_bs:
            tb_initial_acc.append(
                {
                    "general_account_id": line["general_account_id"][0],
                    plan_field: line[plan_field][0],
                    "amount": line["amount"],
                }
            )

        tb_initial_acc = [p for p in tb_initial_acc if p["amount"] != 0]

        tb_period_acc = self._get_tb_period_acc(
            domain=domain,
            date_to=date_to,
            date_from=date_from,
            fields=[plan_field, "general_account_id", "amount"],
            group_by=["general_account_id", plan_field],
            lazy=False,
        )

        total_amount = {}
        total_amount = self._compute_account_amount(
            total_amount,
            tb_initial_acc,
            tb_period_acc,
            "general_account_id",
            plan_field,
            account_ids,
        )

        self._hide_accounts_at_0(company_id, total_amount)

        accounts_ids = list(total_amount.keys())
        accounts_data = self._get_accounts_data(accounts_ids, "general_account_id")

        return total_amount, accounts_data

    @api.model
    def _get_data(
        self,
        account_ids,
        company_id,
        date_to,
        date_from,
        fy_start_date,
        plan_field,
        plan_id,
        group_by_analytic_account,
        financial_account_ids=None,
    ):
        """
        This function gives the report grouped by financial account
        """
        group_by_field = (
            plan_field if group_by_analytic_account else "general_account_id"
        )

        domain = self._get_base_domain(
            account_ids,
            company_id,
            plan_field,
            plan_id,
            group_by_field,
            financial_account_ids=financial_account_ids,
        )

        accounts_domain = [("company_id", "=", company_id)]
        if account_ids:
            accounts_domain += [("id", "in", account_ids)]

        if group_by_field == "general_account_id":
            accounts = self.env["account.account"].search(accounts_domain)
        else:
            accounts = self.env["account.analytic.account"].search(accounts_domain)
        tb_initial_acc = []

        for account in accounts:
            tb_initial_acc.append({"account_id": account.id, "amount": 0.0})

        tb_initial_acc_bs = self._get_tb_initial_acc_bs(
            domain=domain,
            date_from=date_from,
            fy_start_date=fy_start_date,
            fields=[plan_field, "general_account_id", "amount"],
            group_by=[group_by_field],
        )
        for account_rg in tb_initial_acc_bs:
            element = list(
                filter(
                    lambda acc_dict: acc_dict["account_id"]
                    == account_rg[group_by_field][0],
                    tb_initial_acc,
                )
            )
            if element:
                element[0]["amount"] += account_rg["amount"]

        tb_initial_acc = [p for p in tb_initial_acc if p["amount"] != 0]

        tb_period_acc = self._get_tb_period_acc(
            domain=domain,
            date_to=date_to,
            date_from=date_from,
            fields=[plan_field, "general_account_id", "amount"],
            group_by=[group_by_field],
        )

        total_amount = {}
        total_amount = self._compute_account_amount(
            total_amount, tb_initial_acc, tb_period_acc, group_by_field
        )

        self._hide_accounts_at_0(company_id, total_amount)

        accounts_ids = list(total_amount.keys())
        accounts_data = self._get_accounts_data(accounts_ids, group_by_field)

        return total_amount, accounts_data

    def _get_base_total_by_acc_type_select(self, include_both_accounts, plan_field):
        if include_both_accounts:
            return f"""
            SELECT aa.account_type, aal.{plan_field}, sum(amount)
            FROM account_analytic_line AS aal
            INNER JOIN account_account AS aa ON aa.id = aal.general_account_id
            """
        return """
        SELECT aa.account_type, sum(amount)
        FROM account_analytic_line AS aal
        INNER JOIN account_account AS aa ON aa.id = aal.general_account_id
        """

    def _get_base_total_by_acc_type_where(
        self, company_id, account_ids, plan_field, financial_account_ids=None
    ):
        account_ids_where = (
            f"AND aal.{plan_field} in ({','.join(map(str, account_ids))})"
            if account_ids
            else ""
        )
        archives_account_ids = self._get_archived_account_ids(company_id)
        acrhived_account_ids_where = (
            f"AND aal.{plan_field} not in ({','.join(map(str, archives_account_ids))})"
            if archives_account_ids
            else ""
        )
        financial_account_ids_where = (
            f"""AND aal.general_account_id in
            ({','.join(map(str, financial_account_ids))})"""
            if financial_account_ids
            else ""
        )

        return f"""
        WHERE aal.company_id = {company_id}
        {account_ids_where}
        {acrhived_account_ids_where}
        {financial_account_ids_where}
        AND aal.{plan_field} is not null
        """

    def _get_base_total_acc_type_group_by(self, include_both_accounts, plan_field):
        if include_both_accounts:
            return f"""
            GROUP BY aa.account_type, aal.{plan_field}
            """
        return """
        GROUP BY aa.account_type
        """

    def _get_account_type_mapping(self):
        return dict(
            self.env["account.account"].fields_get(allfields=["account_type"])[
                "account_type"
            ]["selection"]
        )

    def _map_accounts_type_by_name(
        self, results, account_type_mapping, balance_type, include_both_accounts
    ):
        result_dict = {}

        # If balance type its period we need to make a specific key for the account_ids
        # To have the amount splitted by financial account and analytic account
        if balance_type == "total_period_balance" and include_both_accounts:
            key_format = "{}|{}"
        else:
            key_format = "{}"

        for result in results:
            if len(result) == 3:
                account_type, account_id, total = result
            elif len(result) == 2:
                account_type, total = result
                account_id = None
            else:
                continue

            account_type_name = account_type_mapping.get(account_type, account_type)

            if include_both_accounts and account_id is not None:
                key = key_format.format(account_type_name, account_id)
            else:
                key = key_format.format(account_type_name)

            if key in result_dict:
                result_dict[key] += total
            else:
                result_dict[key] = total

        return result_dict

    def _get_total_initial_by_acc_type(
        self,
        base_select,
        base_where,
        base_group_by,
        date_from,
        fy_start_date,
    ):
        query = f"""
            {base_select}
            {base_where}
            AND aal.date < %s
            AND aal.date >= %s
            {base_group_by}
        """
        params = [date_from, fy_start_date]
        self.env.cr.execute(query, params)

        return self.env.cr.fetchall()

    def _get_total_period_by_acc_type(
        self,
        base_select,
        base_where,
        base_group_by,
        date_from,
        date_to,
    ):
        query = f"""
            {base_select}
            {base_where}
            AND aal.date >= %s
            AND aal.date <= %s
            {base_group_by}
        """
        params = [date_from, date_to]
        self.env.cr.execute(query, params)

        return self.env.cr.fetchall()

    def _update_balance_by_account_type(
        self, balance_type, totals_by_acc_type, totals_dict
    ):
        for acc_type in totals_by_acc_type:
            totals_dict[acc_type][balance_type] = totals_by_acc_type[acc_type]
            totals_dict[acc_type]["total_ending_balance"] += totals_by_acc_type[
                acc_type
            ]

    def _get_totals_by_acc_type(
        self,
        company_id,
        account_ids,
        date_from,
        date_to,
        plan_field,
        group_by_analytic_account,
        include_both_accounts,
        fy_start_date,
        financial_account_ids=None,
    ):
        """
        This function calculates and returns the totals
        for each account type, providing greater analytical
        precision for the report.
        Period balance will change if the report includes
        the analytic accounts too.
        ex:
                    Inital Balance | Period Balance | Ending Balance
            Income:       1.250€            250€            1.500€
            Epxense:       -500€           -125€            -625€
        """
        account_type_mapping = self._get_account_type_mapping()
        base_select = self._get_base_total_by_acc_type_select(
            include_both_accounts, plan_field
        )
        base_where = self._get_base_total_by_acc_type_where(
            company_id, account_ids, plan_field, financial_account_ids
        )
        base_group_by = self._get_base_total_acc_type_group_by(
            include_both_accounts, plan_field
        )

        account_types_total_dict = {
            account_type_name: self._get_total_amounts_dict(include_both_accounts)
            for _account_type, account_type_name in account_type_mapping.items()
        }
        for _account_type, balances in account_types_total_dict.items():
            for account_id in account_ids:
                # Si tenemos que incluir los dos tipos de cuentas entonces
                # Debemos crear un subapartado por cada cuenta
                if include_both_accounts:
                    if account_id not in balances["total_period_balance"]:
                        balances["total_period_balance"][account_id] = 0
                else:
                    balances["total_period_balance"] = 0

        total_initial_by_acc_type = self._get_total_initial_by_acc_type(
            base_select, base_where, base_group_by, date_from, fy_start_date
        )

        total_period_by_acc_type = self._get_total_period_by_acc_type(
            base_select,
            base_where,
            base_group_by,
            date_from,
            date_to,
        )

        total_initial_by_acc_type = self._map_accounts_type_by_name(
            total_initial_by_acc_type,
            account_type_mapping,
            "total_initial_balance",
            include_both_accounts,
        )
        total_period_by_acc_type = self._map_accounts_type_by_name(
            total_period_by_acc_type,
            account_type_mapping,
            "total_period_balance",
            include_both_accounts,
        )

        if include_both_accounts:
            for key, value in total_period_by_acc_type.items():
                account_type, account_id = key.split("|")
                account_id = int(account_id)
                if (
                    account_id
                    not in account_types_total_dict[account_type][
                        "total_period_balance"
                    ].keys()
                ):
                    account_types_total_dict[account_type]["total_period_balance"][
                        account_id
                    ] = 0
                account_types_total_dict[account_type]["total_period_balance"][
                    account_id
                ] += value
                account_types_total_dict[account_type]["total_ending_balance"] += value
        else:
            self._update_balance_by_account_type(
                "total_period_balance",
                total_period_by_acc_type,
                account_types_total_dict,
            )

        self._update_balance_by_account_type(
            "total_initial_balance", total_initial_by_acc_type, account_types_total_dict
        )

        # Deletes account types with 0 amounts
        filtered_account_types_total_dict = {
            account_type_name: balances
            for account_type_name, balances in account_types_total_dict.items()
            if balances["total_ending_balance"]
        }

        return filtered_account_types_total_dict

    def _get_report_values(self, docids, data):
        wizard_id = data["wizard_id"]
        company = self.env["res.company"].browse(data["company_id"])

        account_codes = self._get_account_codes(data["account_ids"])
        account_code_list = self._clean_account_codes(account_codes)
        financial_account_ids = data["account_account_ids"]

        if (
            data["account_ids"]
            and not data["group_by_analytic_account"]
            and not data["show_hierarchy"]
        ):
            total_amount, accounts_data = self._get_data_splited_by_accounts(
                data["account_ids"],
                data["company_id"],
                data["date_to"],
                data["date_from"],
                data["fy_start_date"],
                data["plan_field"],
                data["plan_id"],
                financial_account_ids=financial_account_ids,
            )
            include_both_accounts = True
        else:
            total_amount, accounts_data = self._get_data(
                data["account_ids"],
                data["company_id"],
                data["date_to"],
                data["date_from"],
                data["fy_start_date"],
                data["plan_field"],
                data["plan_id"],
                data["group_by_analytic_account"],
                financial_account_ids=financial_account_ids,
            )
            include_both_accounts = False

        totals_by_acc_type = self._get_totals_by_acc_type(
            data["company_id"],
            data["account_ids"],
            data["date_from"],
            data["date_to"],
            data["plan_field"],
            data["group_by_analytic_account"],
            include_both_accounts,
            data["fy_start_date"],
            financial_account_ids=financial_account_ids,
        )

        total_amounts = self._get_total_amounts_dict(include_both_accounts)
        self._update_accounts_data(
            accounts_data,
            total_amount,
            total_amounts,
            include_both_accounts=include_both_accounts,
            account_ids=data["account_ids"],
        )
        trial_balance = self._get_trial_balance(
            accounts_data, total_amount, data["show_hierarchy"]
        )

        return self._prepare_report_values(
            wizard_id,
            company,
            data,
            trial_balance,
            total_amount,
            accounts_data,
            account_codes,
            account_code_list,
            total_amounts,
            totals_by_acc_type,
            financial_account_ids,
        )

    def _prepare_report_values(
        self,
        wizard_id,
        company,
        data,
        trial_balance,
        total_amount,
        accounts_data,
        account_codes,
        account_code_list,
        total_amounts,
        totals_by_acc_type,
        financial_account_ids,
    ):
        return {
            "doc_ids": [wizard_id],
            "doc_model": "ac.trial.balance.report.wizard",
            "docs": self.env["ac.trial.balance.report.wizard"].browse(wizard_id),
            "company_name": company.display_name,
            "currency_name": company.currency_id.name,
            "date_from": data["date_from"],
            "date_to": data["date_to"],
            "trial_balance": trial_balance,
            "total_amount": total_amount,
            "accounts_data": accounts_data,
            "plan_name": data["plan_name"],
            "plan_field": data["plan_field"],
            "group_by_analytic_account": data["group_by_analytic_account"],
            "show_hierarchy": data["show_hierarchy"],
            "limit_hierarchy_level": data["limit_hierarchy_level"],
            "show_hierarchy_level": data["hierarchy_level"],
            "account_codes": account_codes,
            "account_code_list": account_code_list,
            "account_ids": data["account_ids"],
            "show_months": data["show_months"],
            "total_amounts": total_amounts,
            "archived_accounts": tuple(self._get_archived_account_ids(company.id)),
            "totals_by_acc_type": totals_by_acc_type,
            "financial_account_ids": financial_account_ids,
        }
