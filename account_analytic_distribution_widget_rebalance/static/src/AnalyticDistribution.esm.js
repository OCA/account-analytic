/** @odoo-module **/
/*
    Copyright 2025 Camptocamp SA (https://www.camptocamp.com).
    License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
*/

import {AnalyticDistribution} from "@analytic/components/analytic_distribution/analytic_distribution";
import {patch} from "@web/core/utils/patch";
import {roundDecimals} from "@web/core/utils/numbers";

patch(AnalyticDistribution.prototype, {
    _computeRebalanceAmount(line) {
        const linePlansData = line.analyticAccounts.filter((item) => item.accountId);
        // If the line has no plans, or more than one plan, we can't rebalance.
        // We only support the case with a single plan/account per line.
        if (linePlansData.length !== 1) {
            return false;
        }
        const planId = linePlansData[0].planId;
        const planTotal = this.planTotals()[planId].value;
        return roundDecimals(1 - planTotal, this.decimalPrecision.digits[1] + 2);
    },
    canRebalanceLine(lineIndex) {
        const line = this.state.formattedData[lineIndex];
        return Boolean(this._computeRebalanceAmount(line));
    },
    rebalanceLine(lineIndex) {
        const line = this.state.formattedData[lineIndex];
        const rebalanceAmount = this._computeRebalanceAmount(line);
        if (rebalanceAmount) {
            line.percentage += rebalanceAmount;
        }
    },
});
