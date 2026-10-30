/* @odoo-module */
import {
    contains,
    defineModels,
    fields,
    models,
    mountView,
    onRpc,
} from "@web/../tests/web_test_helpers";
import {describe, expect, test} from "@odoo/hoot";
import {animationFrame} from "@odoo/hoot-mock";
import {mailModels} from "@mail/../tests/mail_test_helpers";

/**
 * Models and data for the analytic distribution rebalance tests.
 * Reproducing the serverData from the original QUnit tests.
 */

class AnalyticAccount extends models.Model {
    _name = "account.analytic.account";
    name = fields.Char();
    plan_id = fields.Many2one({relation: "plan"});
    root_plan_id = fields.Many2one({relation: "plan"});
    color = fields.Integer();
    code = fields.Char();
    partner_id = fields.Many2one({relation: "partner"});

    _records = [
        {id: 1, name: "RD", color: 1, root_plan_id: 2, plan_id: 2},
        {id: 2, name: "HR", color: 1, root_plan_id: 2, plan_id: 2},
        {id: 3, name: "FI", color: 1, root_plan_id: 2, plan_id: 2},
        {id: 4, name: "Time Off", color: 2, root_plan_id: 1, plan_id: 1},
        {id: 5, name: "Operating Costs", color: 2, root_plan_id: 1, plan_id: 1},
    ];
}

class Plan extends models.Model {
    _name = "plan";
    name = fields.Char();
    applicability = fields.Selection({
        selection: [
            ["mandatory", "Mandatory"],
            ["optional", "Options"],
            ["unavailable", "Unavailable"],
        ],
    });
    color = fields.Integer();
    all_account_count = fields.Integer();
    parent_id = fields.Many2one({relation: "plan"});
    column_name = fields.Char();

    _records = [
        {
            id: 1,
            name: "Internal",
            applicability: "optional",
            all_account_count: 2,
            column_name: "x_plan1_id",
        },
        {
            id: 2,
            name: "Departments",
            applicability: "mandatory",
            all_account_count: 3,
            column_name: "x_plan2_id",
        },
    ];
}

class Company extends models.Model {
    _name = "res.company";
    name = fields.Char();
    _records = [{id: 1, name: "YourCompany"}];
}

class Aml extends models.Model {
    _name = "aml";
    label = fields.Char();
    amount = fields.Float();
    analytic_distribution = fields.Json();
    move_id = fields.Many2one({relation: "move"});
    analytic_precision = fields.Integer();
    company_id = fields.Many2one({relation: "res.company"});

    _records = [
        {
            id: 1,
            label: "Test 1",
            amount: 100.0,
            analytic_distribution: {1: 100, 2: 20, 3: 30},
            analytic_precision: 3,
            company_id: 1,
        },
        {
            id: 2,
            label: "Test 2",
            amount: 100.0,
            analytic_distribution: {1: 40, "2,4": 30, "3,5": 40},
            analytic_precision: 3,
            company_id: 1,
        },
    ];
}

class Partner extends models.Model {
    _name = "partner";
    name = fields.Char();
    _records = [{id: 1, name: "Great Partner"}];
}

class Move extends models.Model {
    _name = "move";
    line_ids = fields.One2many({relation: "aml", relation_field: "move_id"});
    _records = [{id: 1, display_name: "INV0001", line_ids: [1]}];
}

defineModels({
    ...mailModels,
    AnalyticAccount,
    Plan,
    Aml,
    Partner,
    Move,
    Company,
});

describe("account_analytic_distribution_widget_rebalance", () => {
    test("analytic distribution rebalance first line", async () => {
        onRpc("account.analytic.plan", "get_relevant_plans", () => {
            return [
                {
                    id: 1,
                    name: "Internal",
                    applicability: "optional",
                    all_account_count: 2,
                    column_name: "x_plan1_id",
                },
                {
                    id: 2,
                    name: "Departments",
                    applicability: "mandatory",
                    all_account_count: 3,
                    column_name: "x_plan2_id",
                },
            ];
        });

        await mountView({
            type: "form",
            resModel: "aml",
            resId: 1,
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
        });

        // Open the popup
        await contains(".o_field_analytic_distribution .o_input_dropdown").click();
        expect(".analytic_distribution_popup").toHaveCount(1, {
            message: "popup should be visible",
        });

        // The total for Departments is 150%
        // In Hoot, we use text content matchers or query selectores
        expect(
            ".analytic_distribution_popup thead th:nth-of-type(2) span:last-of-type"
        ).toHaveText("150%", {
            message: "total should be 150%",
        });

        // Rebalance is possible on all the lines
        expect(
            ".analytic_distribution_popup tr[name] .rebalanceColumn > span"
        ).toHaveCount(3, {
            message: "rebalance should be possible on all lines",
        });

        // Rebalance the first line
        const firstLineSelector = ".analytic_distribution_popup tr[name]:first-child";
        expect(`${firstLineSelector} div[name='percentage'] input`).toHaveValue("100", {
            message: "percentage should be 100% before rebalancing",
        });

        document.querySelector(`${firstLineSelector} .rebalanceColumn > span`).click();
        await animationFrame();

        expect(`${firstLineSelector} div[name='percentage'] input`).toHaveValue("50", {
            message: "percentage should be 50% after rebalancing",
        });

        // Rebalance should be hidden on all lines
        expect(
            ".analytic_distribution_popup tr[name] .rebalanceColumn > span"
        ).toHaveCount(0, {
            message: "rebalance should be hidden on all lines after rebalance",
        });
    });

    test("analytic distribution rebalance not possible if multiple plans", async () => {
        onRpc("account.analytic.plan", "get_relevant_plans", () => {
            return [
                {
                    id: 1,
                    name: "Internal",
                    applicability: "optional",
                    all_account_count: 2,
                    column_name: "x_plan1_id",
                },
                {
                    id: 2,
                    name: "Departments",
                    applicability: "mandatory",
                    all_account_count: 3,
                    column_name: "x_plan2_id",
                },
            ];
        });

        await mountView({
            type: "form",
            resModel: "aml",
            resId: 2,
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
        });

        // Open the popup
        await contains(".o_field_analytic_distribution .o_input_dropdown").click();
        expect(".analytic_distribution_popup").toHaveCount(1, {
            message: "popup should be visible",
        });

        // The total for Internal is 70% and Departments is 110%
        expect(
            ".analytic_distribution_popup thead th:nth-of-type(1) span:first-of-type"
        ).toHaveText("Internal");
        expect(
            ".analytic_distribution_popup thead th:nth-of-type(1) span:last-of-type"
        ).toHaveText("70%", {
            message: "Internal should be 70%",
        });
        expect(
            ".analytic_distribution_popup thead th:nth-of-type(2) span:first-of-type"
        ).toHaveText("Departments");
        expect(
            ".analytic_distribution_popup thead th:nth-of-type(2) span:last-of-type"
        ).toHaveText("110%", {
            message: "Departments should be 110%",
        });

        // Rebalance is possible only on the first line, because it has only one plan
        const linesSelectors = [
            ".analytic_distribution_popup tr[name]:nth-child(1)",
            ".analytic_distribution_popup tr[name]:nth-child(2)",
            ".analytic_distribution_popup tr[name]:nth-child(3)",
        ];

        expect(`${linesSelectors[0]} .rebalanceColumn > span`).toHaveCount(1, {
            message: "rebalance should be possible on the first line",
        });
        expect(`${linesSelectors[1]} .rebalanceColumn > span`).toHaveCount(0, {
            message: "rebalance should be hidden on the second line",
        });
        expect(`${linesSelectors[2]} .rebalanceColumn > span`).toHaveCount(0, {
            message: "rebalance should be hidden on the third line",
        });

        // Rebalance the first line
        document.querySelector(`${linesSelectors[0]} .rebalanceColumn > span`).click();
        await animationFrame();

        expect(`${linesSelectors[0]} div[name='percentage'] input`).toHaveValue("30", {
            message: "percentage should be 30% after rebalancing",
        });

        // Rebalance should be hidden on all lines
        expect(
            ".analytic_distribution_popup tr[name] .rebalanceColumn > span"
        ).toHaveCount(0, {
            message: "rebalance should be hidden on all lines after rebalance",
        });

        // The total for Internal is 70% and Departments is 100%
        expect(
            ".analytic_distribution_popup thead th:nth-of-type(1) span:last-of-type"
        ).toHaveText("70%", {
            message: "Internal should remain 70%",
        });
        expect(
            ".analytic_distribution_popup thead th:nth-of-type(2) span:last-of-type"
        ).toHaveText("100%", {
            message: "Departments should be 100%",
        });
    });
});
