/** @odoo-module **/
/* global QUnit */

import {AnalyticDistribution} from "@analytic/components/analytic_distribution/analytic_distribution";

QUnit.module("AnalyticDistribution - plan order by sequence");

QUnit.test("sortedList sorts strictly by sequence", function (assert) {
    assert.expect(1);

    const ctx = {
        list: {
            1: {id: 1, name: "Projects", sequence: 20},
            2: {id: 2, name: "Departments", sequence: 10},
            3: {id: 3, name: "Misc", sequence: 30},
        },
    };

    const getter = Object.getOwnPropertyDescriptor(
        AnalyticDistribution.prototype,
        "sortedList"
    ).get;

    const result = getter.call(ctx);
    const order = result.map((p) => p.id);

    assert.deepEqual(order, [2, 1, 3], "Plans are ordered 10 < 20 < 30");
});
