/** @odoo-module **/

import {patch} from "@web/core/utils/patch";
import {AnalyticDistribution} from "@analytic/components/analytic_distribution/analytic_distribution";

patch(AnalyticDistribution.prototype, "analytic_distribution.sort_plans_by_sequence", {
    get sortedList() {
        return Object.values(this.list).sort((a, b) => a.sequence - b.sequence);
    },
});

patch(AnalyticDistribution.prototype, "analytic_distribution.sort_tags_by_plan_order", {
    get tags() {
        const base = this._super();
        const orderIdx = Object.create(null);
        this.sortedList.forEach((plan, i) => {
            orderIdx[plan.id] = i;
        });
        return base.slice().sort((a, b) => orderIdx[a.group_id] - orderIdx[b.group_id]);
    },
});
