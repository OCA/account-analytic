/** @odoo-module **/
/*
    Copyright 2025 Camptocamp SA (https://www.camptocamp.com).
    License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
*/

import {click, getFixture} from "@web/../tests/helpers/utils";
import {makeView, setupViewRegistries} from "@web/../tests/views/helpers";
import {batchedOrmService} from "@analytic/services/batched_orm_service";
import {registry} from "@web/core/registry";
const {QUnit} = window;

let serverData = {};
let target = null;

QUnit.module("Analytic", (hooks) => {
    hooks.beforeEach(() => {
        target = getFixture();
        serverData = {
            models: {
                "account.analytic.account": {
                    fields: {
                        plan_id: {string: "Plan", type: "many2one", relation: "plan"},
                        root_plan_id: {
                            string: "Root Plan",
                            type: "many2one",
                            relation: "plan",
                        },
                        color: {string: "Color", type: "integer"},
                        code: {string: "Ref", type: "string"},
                        partner_id: {
                            string: "Partner",
                            type: "many2one",
                            relation: "partner",
                        },
                    },
                    records: [
                        {id: 1, color: 1, root_plan_id: 2, plan_id: 2, name: "RD"},
                        {id: 2, color: 1, root_plan_id: 2, plan_id: 2, name: "HR"},
                        {id: 3, color: 1, root_plan_id: 2, plan_id: 2, name: "FI"},
                        {
                            id: 4,
                            color: 2,
                            root_plan_id: 1,
                            plan_id: 1,
                            name: "Time Off",
                        },
                        {
                            id: 5,
                            color: 2,
                            root_plan_id: 1,
                            plan_id: 1,
                            name: "Operating Costs",
                        },
                    ],
                },
                plan: {
                    fields: {
                        applicability: {
                            string: "Applicability",
                            type: "selection",
                            selection: [
                                ["mandatory", "Mandatory"],
                                ["optional", "Options"],
                                ["unavailable", "Unavailable"],
                            ],
                        },
                        color: {string: "Color", type: "integer"},
                        all_account_count: {type: "integer"},
                        parent_id: {type: "many2one", relation: "plan"},
                    },
                    records: [
                        {
                            id: 1,
                            name: "Internal",
                            applicability: "optional",
                            all_account_count: 2,
                        },
                        {
                            id: 2,
                            name: "Departments",
                            applicability: "mandatory",
                            all_account_count: 3,
                        },
                    ],
                },
                aml: {
                    fields: {
                        label: {string: "Label", type: "char"},
                        amount: {string: "Amount", type: "float"},
                        analytic_distribution: {string: "Analytic", type: "json"},
                        move_id: {
                            string: "Account Move",
                            type: "many2one",
                            relation: "move",
                        },
                        analytic_precision: {
                            string: "Analytic Precision",
                            type: "integer",
                        },
                    },
                    records: [
                        {
                            id: 1,
                            label: "Test 1",
                            amount: 100.0,
                            analytic_distribution: {1: 100, 2: 20, 3: 30},
                            analytic_precision: 3,
                        },
                        {
                            id: 2,
                            label: "Test 2",
                            amount: 100.0,
                            analytic_distribution: {1: 40, "2,4": 30, "3,5": 40},
                            analytic_precision: 3,
                        },
                    ],
                },
                partner: {
                    fields: {
                        name: {string: "Name", type: "char"},
                    },
                    records: [{id: 1, name: "Great Partner"}],
                },
                move: {
                    fields: {
                        line_ids: {
                            string: "Move Lines",
                            type: "one2many",
                            relation: "aml",
                            relation_field: "move_line_id",
                        },
                    },
                    records: [{id: 1, display_name: "INV0001", line_ids: [1]}],
                },
            },
            views: {
                "account.analytic.account,false,search": `<search/>`,
                "account.analytic.account,analytic.view_account_analytic_account_list_select,list": `
                    <tree>
                        <field name="name"/>
                    </tree>
                `,
            },
        };

        setupViewRegistries();
        registry.category("services").add("batchedOrm", batchedOrmService);
    });

    QUnit.module("AnalyticDistributionRebalance");

    QUnit.test("analytic distribution rebalance first line", async function (assert) {
        await makeView({
            type: "form",
            resModel: "aml",
            resId: 1,
            serverData,
            arch: `
                <form>
                    <sheet>
                        <group>
                            <field name="label"/>
                            <field name="analytic_distribution" widget="analytic_distribution"/>
                            <field name="amount"/>
                        </group>
                    </sheet>
                </form>`,
            mockRPC(route, {method, model}) {
                if (
                    method === "get_relevant_plans" &&
                    model === "account.analytic.plan"
                ) {
                    return Promise.resolve(
                        serverData.models.plan.records.filter(
                            (r) => !r.parent_id && r.applicability !== "unavailable"
                        )
                    );
                }
            },
        });

        // Open the popup
        const field = target.querySelector(".o_field_analytic_distribution");
        await click(field, ".o_input_dropdown");
        assert.containsN(
            target,
            ".analytic_distribution_popup",
            1,
            "popup should be visible"
        );
        const popup = target.querySelector(".analytic_distribution_popup");
        // The total for Departments is 150%
        assert.strictEqual(
            popup.querySelector("thead th:nth-of-type(2) span:last-of-type")
                .textContent,
            "150%",
            "total should be 150%"
        );
        // Rebalance is possible on all the lines
        for (const line of popup.querySelectorAll("tr[name]")) {
            assert.containsN(
                line,
                ".rebalanceColumn > span",
                1,
                "rebalance should be possible on this line"
            );
        }
        // Rebalance the first line
        const firstLine = popup.querySelector("tr[name]");
        assert.strictEqual(
            firstLine.querySelector("div[name='percentage'] input").value,
            "100",
            "percentage should be 100% before rebalancing"
        );
        await click(firstLine.querySelector(".rebalanceColumn > span"));
        assert.strictEqual(
            firstLine.querySelector("div[name='percentage'] input").value,
            "50",
            "percentage should be 50% after rebalancing"
        );
        // Rebalance should be hidden on all lines
        for (const line of popup.querySelectorAll("tr[name]")) {
            assert.containsNone(
                line,
                ".rebalanceColumn > span",
                "rebalance should be hidden on this line"
            );
        }
    });

    QUnit.test(
        "analytic distribution rebalance not possible if multiple plans",
        async function (assert) {
            await makeView({
                type: "form",
                resModel: "aml",
                resId: 2,
                serverData,
                arch: `
                <form>
                    <sheet>
                        <group>
                            <field name="label"/>
                            <field name="analytic_distribution" widget="analytic_distribution"/>
                            <field name="amount"/>
                        </group>
                    </sheet>
                </form>`,
                mockRPC(route, {method, model}) {
                    if (
                        method === "get_relevant_plans" &&
                        model === "account.analytic.plan"
                    ) {
                        return Promise.resolve(
                            serverData.models.plan.records.filter(
                                (r) => !r.parent_id && r.applicability !== "unavailable"
                            )
                        );
                    }
                },
            });

            // Open the popup
            const field = target.querySelector(".o_field_analytic_distribution");
            await click(field, ".o_input_dropdown");
            assert.containsN(
                target,
                ".analytic_distribution_popup",
                1,
                "popup should be visible"
            );
            const popup = target.querySelector(".analytic_distribution_popup");
            // The total for Internal is 70% and Departments is 110%
            assert.strictEqual(
                popup.querySelector("thead th:nth-of-type(1) span:first-of-type")
                    .textContent,
                "Internal"
            );
            assert.strictEqual(
                popup.querySelector("thead th:nth-of-type(1) span:last-of-type")
                    .textContent,
                "70%",
                "Internal should be 70%"
            );
            assert.strictEqual(
                popup.querySelector("thead th:nth-of-type(2) span:first-of-type")
                    .textContent,
                "Departments"
            );
            assert.strictEqual(
                popup.querySelector("thead th:nth-of-type(2) span:last-of-type")
                    .textContent,
                "110%",
                "Departments should be 110%"
            );
            // Rebalance is possible only on the first line, because it has only one plan
            const lines = popup.querySelectorAll("tr[name]");
            assert.containsN(
                lines[0],
                ".rebalanceColumn > span",
                1,
                "rebalance should be possible on the first line"
            );
            assert.containsN(
                lines[1],
                ".rebalanceColumn > span",
                0,
                "rebalance should be hidden on the second line"
            );
            assert.containsN(
                lines[2],
                ".rebalanceColumn > span",
                0,
                "rebalance should be hidden on the third line"
            );
            // Rebalance the first line
            await click(lines[0].querySelector(".rebalanceColumn > span"));
            assert.strictEqual(
                lines[0].querySelector("div[name='percentage'] input").value,
                "30",
                "percentage should be 30% after rebalancing"
            );
            // Rebalance should be hidden on all lines
            for (const line of lines) {
                assert.containsNone(
                    line,
                    ".rebalanceColumn > span",
                    "rebalance should be hidden on this line"
                );
            }
            // The total for Internal is 60% and Departments is 100%
            assert.strictEqual(
                popup.querySelector("thead th:nth-of-type(1) span:last-of-type")
                    .textContent,
                "70%",
                "Internal should remain 70%"
            );
            assert.strictEqual(
                popup.querySelector("thead th:nth-of-type(2) span:last-of-type")
                    .textContent,
                "100%",
                "Departments should be 100%"
            );
        }
    );
});
