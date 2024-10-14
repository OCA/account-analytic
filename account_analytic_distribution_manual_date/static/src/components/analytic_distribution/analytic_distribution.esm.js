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
        const invoiceDate = this.state_invoice_date.date;

        domain.push(
            "|",
            "&",
            ["start_date", "<=", invoiceDate],
            ["end_date", ">=", invoiceDate],

            "|",
            "&",
            ["start_date", "<=", invoiceDate],
            ["end_date", "=", false],

            "|",
            "&",
            ["start_date", "=", false],
            ["end_date", ">=", invoiceDate],

            "&",
            ["start_date", "=", false],
            ["end_date", "=", false]
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
