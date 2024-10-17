/** @odoo-module **/
// Copyright 2024 (APSL - Nagarro) Bernat Obrador
// License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import {AnalyticDistribution} from "@analytic/components/analytic_distribution/analytic_distribution";
import {patch} from "@web/core/utils/patch";
const {useState} = owl;

patch(AnalyticDistribution.prototype, {
    setup() {
        super.setup(...arguments);

        this.state_invoice_date = useState({
            date: this.getDate(),
        });
    },

    async fetchAnalyticDistributionManual(domain, limit = null) {
        await this.refreshInvoiceDate();

        domain.push(
            ["start_date", "<=", this.state_invoice_date.date],
            ["end_date", ">=", this.state_invoice_date.date]
        );

        return super.fetchAnalyticDistributionManual(domain, limit);
    },
    async refreshInvoiceDate() {
        if (this.state_invoice_date.date !== this.getDate()) {
            this.state_invoice_date.date = this.getDate();
        }
    },
    async processSelectedOption(selected_option) {
        await super.processSelectedOption(selected_option);
        // This solves a bug if saiving the record with the widget open
        super.save();
    },
    getDate() {
        try {
            const parentRecordData = this.props.record._parentRecord.data || {};

            if (this.props.record.model.config.resModel === "account.move") {
                return (
                    parentRecordData.invoice_date || parentRecordData.date || new Date()
                );
            }
            return new Date();
        } catch (error) {
            return new Date();
        }
    },
});
