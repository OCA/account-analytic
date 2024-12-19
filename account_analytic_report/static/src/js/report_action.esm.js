// /** @odoo-module **/
import {ReportAction} from "@web/webclient/actions/reports/report_action";
import {patch} from "@web/core/utils/patch";
import {useEnrichWithActionLinks} from "./report.esm";

const MODULE_NAME = "account_analytic_report";

patch(ReportAction.prototype, {
    setup() {
        super.setup(...arguments);
        this.isAccountAnalyticReport = this.props.report_name.startsWith(
            `${MODULE_NAME}.`
        );
        useEnrichWithActionLinks(this.iframe);
    },

    export_analytic_report() {
        this.action.doAction({
            type: "ir.actions.report",
            report_type: "xlsx",
            report_name: this._get_xlsx_analytic_name(this.props.report_name),
            report_file: this._get_xlsx_analytic_name(this.props.report_file),
            data: this.props.data || {},
            context: this.props.context || {},
            display_name: this.title,
        });
    },

    /**
     * @param {String} str
     * @returns {String}
     */
    _get_xlsx_analytic_name(str) {
        if (typeof str !== "string") {
            return str;
        }
        const parts = str.split(".");
        return `a_a_r.report_${parts[parts.length - 1]}_xlsx`;
    },
});
