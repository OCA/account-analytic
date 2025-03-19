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
    async willUpdateRecord(record) {
        await super.willUpdateRecord(record);
        const current_manual_distribution_id = this.state_manual_distribution.id;
        const new_manual_distribution_id = record.data.manual_distribution_id
            ? this.props.record.data.manual_distribution_id[0]
            : 0;
        const manual_distribution_Changed =
            current_manual_distribution_id !== new_manual_distribution_id;
        // If record is not dirty we need need to force the update of the
        // manual distribution if it has changed
        if (manual_distribution_Changed && !record.dirty) {
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

    planSummaryTags() {
        let tags = super.planSummaryTags(...arguments);
        if (this.state_manual_distribution.id) {
            // Remove the delete button from tags
            // it will be added only to the manual distribution tag
            /* eslint-disable-next-line no-unused-vars */
            tags = tags.map(({onDelete, ...rest}) => rest);
            tags.unshift({
                id: this.nextId++,
                text: this.state_manual_distribution.label,
                onDelete: this.editingRecord ? () => this.deleteManualTag() : undefined,
            });
        }

        return tags;
    },

    deleteManualTag() {
        this.state_manual_distribution.id = 0;
        this.state_manual_distribution.label = "";
        this.state_manual_distribution.analytic_distribution = [];
        // Clear all distribution
        this.state.formattedData = [];
        this.props.record.update({
            [this.props.name]: this.dataToJson(),
            manual_distribution_id: false,
        });
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
        const formattedLines = [];
        for (const [accountIds, percentage] of Object.entries(
            selected_option.analytic_distribution
        )) {
            const ids = accountIds.split(",").map((id) => parseInt(id, 10));
            const analyticAccountDict = ids.length
                ? await this.fetchAnalyticAccounts([["id", "in", ids]])
                : [];
            const lineToAdd = {
                id: this.nextId++,
                analyticAccounts: this.plansToArray(),
                percentage: percentage / 100,
            };
            for (const id of ids) {
                const account = analyticAccountDict[id];

                if (account) {
                    lineToAdd.analyticAccounts.push({
                        accountId: id,
                        accountDisplayName: account.display_name,
                        planColor: account.color,
                        accountRootPlanId: account.root_plan_id[0],
                        planId: account.root_plan_id[0],
                        planName: account.root_plan_id[1],
                    });
                }
            }
            formattedLines.push(lineToAdd);
        }
        this.state.formattedData.push(...formattedLines);
    },
    async onSelectDistributionManual(option) {
        const selected_option = Object.getPrototypeOf(option);

        this.state_manual_distribution.id = selected_option.value;
        this.state_manual_distribution.label = selected_option.label;
        this.state_manual_distribution.analytic_distribution =
            selected_option.analytic_distribution;
        // Clear all distribution
        this.state.formattedData = [];

        await this.processSelectedOption(selected_option);
    },
});

AnalyticDistribution.components = {...AnalyticDistribution.components, AutoComplete};
