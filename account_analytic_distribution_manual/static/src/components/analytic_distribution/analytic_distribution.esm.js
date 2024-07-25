/** @odoo-module **/

import {AnalyticDistribution} from "@analytic/components/analytic_distribution/analytic_distribution";
import {patch} from "@web/core/utils/patch";

patch(AnalyticDistribution.prototype, "account_analytic_distribution_manual", {
    // Autocomplete
    sourcesAnalyticDistributionManual() {
        return [
            {
                placeholder: this.env._t("Loading..."),
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
        const options = records.map((result) => ({
            value: result.id,
            label: result.display_name,
            analytic_distribution: result.analytic_distribution,
        }));
        if (!options.length) {
            options.push({
                label: this.env._t("No Analytic Distribution Manual found"),
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
    async onSelectDistributionManual(option) {
        const selected_option = Object.getPrototypeOf(option);
        const account_ids = Object.keys(selected_option.analytic_distribution).map(
            (id) => parseInt(id, 10)
        );
        const analytic_accounts = await this.fetchAnalyticAccounts([
            ["id", "in", account_ids],
        ]);
        // Clear all distribution
        for (const group_id in this.list) {
            this.list[group_id].distribution = [];
        }
        for (const account of analytic_accounts) {
            // Add new tags
            const planId = account.root_plan_id[0];
            const tag = this.newTag(planId);
            tag.analytic_account_id = account.id;
            tag.analytic_account_name = account.display_name;
            tag.percentage = selected_option.analytic_distribution[account.id];
            this.list[planId].distribution.push(tag);
        }

        this.autoFill();
    },
});
