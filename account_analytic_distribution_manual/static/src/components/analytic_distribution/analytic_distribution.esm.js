/** @odoo-module **/

import {AnalyticDistribution} from "@analytic/components/analytic_distribution/analytic_distribution";
import {AutoComplete} from "@web/core/autocomplete/autocomplete";
import {_t} from "@web/core/l10n/translation";
import {patch} from "@web/core/utils/patch";
const {useState} = owl;

patch(AnalyticDistribution.prototype, {
    setup() {
        super.setup(...arguments);
        this.manual_distribution_by_id = {};
        this.state_manual_distribution = useState({
            id: this.props.record.data.manual_distribution_id
                ? this.props.record.data.manual_distribution_id[0]
                : 0,
            label: "",
            analytic_distribution: [],
        });
    },
    async willStart() {
        await super.willStart(...arguments);
        if (this.state_manual_distribution.id) {
            this.refreshManualDistribution(this.state_manual_distribution.id);
        }
    },
    async willUpdate(nextProps) {
        await super.willUpdate(nextProps);
        const record_id = this.props.record.data.id || 0;
        const current_manual_distribution_id = this.state_manual_distribution.id;
        const new_manual_distribution_id = nextProps.record.data.manual_distribution_id
            ? this.props.record.data.manual_distribution_id[0]
            : 0;
        const manual_distribution_Changed =
            current_manual_distribution_id !== new_manual_distribution_id;
        // When record is created, and manual_distribution_id is cleared
        // but user discard changes, we need to refresh the manual distribution
        const force_refresh_discart = new_manual_distribution_id === 0 && record_id > 0;
        if (
            manual_distribution_Changed &&
            (new_manual_distribution_id > 0 || force_refresh_discart)
        ) {
            await this.refreshManualDistribution(new_manual_distribution_id);
        }
    },
    async save() {
        await super.save();
        if (this.state_manual_distribution.id) {
            await this.props.record.update({
                manual_distribution_id: [
                    this.state_manual_distribution.id,
                    this.state_manual_distribution.label,
                ],
            });
        }
    },
    async refreshManualDistribution(manual_distribution_id) {
        if (manual_distribution_id === 0) {
            this.deleteManualTag();
            return;
        }
        const current_record = this.manual_distribution_by_id[manual_distribution_id];
        if (current_record) {
            this.state_manual_distribution.id = current_record.id;
            this.state_manual_distribution.label = current_record.display_name;
            this.state_manual_distribution.analytic_distribution =
                current_record.analytic_distribution;
            return;
        }
        const records = await this.fetchAnalyticDistributionManual([
            ["id", "=", manual_distribution_id],
        ]);
        if (records.length) {
            const record = records[0];
            this.state_manual_distribution.id = record.id;
            this.state_manual_distribution.label = record.display_name;
            this.state_manual_distribution.analytic_distribution =
                record.analytic_distribution;
        } else {
            this.deleteManualTag();
        }
    },
    get tags() {
        let res = super.tags(...arguments);
        if (this.state_manual_distribution.id) {
            // Remove the delete button from tags
            // it will be added only to the manual distribution tag
            /* eslint-disable-next-line no-unused-vars */
            res = res.map(({onDelete, ...rest}) => rest);
            res.unshift({
                id: this.nextId++,
                text: this.state_manual_distribution.label,
                onDelete: this.editingRecord ? () => this.deleteManualTag() : undefined,
            });
        }
        return res;
    },
    deleteManualTag() {
        this.state_manual_distribution = {
            id: 0,
            label: "",
            analytic_distribution: [],
        };
        // Clear all distribution
        this.state.formattedData = [];
    },
    // Autocomplete
    sourcesAnalyticDistributionManual() {
        return [
            {
                placeholder: _t("Loading..."),
                options: (searchTerm) =>
                    this.loadOptionsSourceDistributionManual(searchTerm),
            },
        ];
    },
    async loadOptionsSourceDistributionManual(searchTerm) {
        const searchLimit = 6;
        const records = await this.fetchAnalyticDistributionManual(
            [...this.searchAnalyticDistributionManualDomain(searchTerm)],
            searchLimit + 1
        );
        const options = [];
        for (const record of records) {
            options.push({
                value: record.id,
                label: record.display_name,
                analytic_distribution: record.analytic_distribution,
            });
            this.manual_distribution_by_id[record.id] = record;
        }
        if (!options.length) {
            options.push({
                label: _t("No Analytic Distribution Manual found"),
                classList: "o_m2o_no_result",
                unselectable: true,
            });
        }
        return options;
    },
    async fetchAnalyticDistributionManual(domain, limit = null) {
        const args = {
            domain: domain,
            fields: ["id", "display_name", "analytic_distribution"],
            context: [],
        };
        if (limit) {
            args.limit = limit;
        }
        return await this.orm.call(
            "account.analytic.distribution.manual",
            "search_read",
            [],
            args
        );
    },
    searchAnalyticDistributionManualDomain(searchTerm) {
        const domain = [["name", "ilike", searchTerm]];
        if (this.props.record.data.company_id) {
            domain.push(["company_id", "=", this.props.record.data.company_id[0]]);
        }
        return domain;
    },
    onChangeAutoCompleteDistributionManual(inputValue) {
        if (inputValue === "") {
            this.deleteManualTag();
        }
    },
    async processSelectedOption(selected_option) {
        for (const idsString in selected_option.analytic_distribution) {
            const percentage = selected_option.analytic_distribution[idsString];

            // Parse the IDs of selected_options, converting the key (e.g., "1,3") into an array of IDs [1, 3].
            const idsArray = idsString.split(",").map((id) => parseInt(id, 10));
            const lineToAdd = {
                id: this.nextId++,
                analyticAccounts: this.plansToArray(),
                percentage: percentage / 100,
            };

            for (let i = 0; i < idsArray.length; i++) {
                const accountId = idsArray[i];
                const accountData = await this.getAccountDetails(accountId);
                if (accountData) {
                    lineToAdd.analyticAccounts.push({
                        accountId: accountData.id,
                        accountDisplayName: accountData.display_name,
                        planColor: accountData.color,
                        accountRootPlanId: accountData.root_plan_id[0],
                        planId: accountData.root_plan_id[0],
                        planName: accountData.root_plan_id[1],
                    });
                }
            }
            this.state.formattedData.push(lineToAdd);
        }
    },
    async getAccountDetails(accountId) {
        const record = await this.orm.read(
            "account.analytic.account",
            [accountId],
            ["name", "color", "root_plan_id"]
        );
        const accountDetails = {
            id: accountId,
            display_name: record[0].name,
            color: record[0].color,
            root_plan_id: record[0].root_plan_id,
        };
        return accountDetails;
    },
    async onSelectDistributionManual(option) {
        const selected_option = Object.getPrototypeOf(option);
        this.state_manual_distribution = {
            id: selected_option.value,
            label: selected_option.label,
            analytic_distribution: selected_option.analytic_distribution,
        };
        // Clear all distribution
        this.state.formattedData = [];

        await this.processSelectedOption(selected_option);
    },
});

AnalyticDistribution.components = {...AnalyticDistribution.components, AutoComplete};
