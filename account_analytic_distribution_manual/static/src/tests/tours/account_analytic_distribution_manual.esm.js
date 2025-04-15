import {browser} from "@web/core/browser/browser";
import {registry} from "@web/core/registry";
import {stepUtils} from "@web_tour/tour_service/tour_utils";

registry.category("web_tour.tours").add("account_analytic_distribution_manual", {
    test: true,
    url: "/web",
    steps: () => [
        ...stepUtils.goToAppSteps("account.menu_finance", ""),
        {
            content: "Go to Customers",
            trigger: 'span:contains("Customers")',
            run: "click",
        },
        {
            content: "Go to Invoices",
            trigger: "[data-menu-xmlid='account.menu_action_move_out_invoice_type']",
            run: "click",
        },
        {
            content: "Create new invoice",
            trigger: "button.o_list_button_add",
            run: "click",
        },
        {
            content: "Add Customer",
            trigger:
                'div.o_field_widget.o_field_res_partner_many2one[name="partner_id"] div input',
            run: "edit partner_a",
        },
        {
            content: "Valid Customer",
            trigger: '.ui-menu-item a:contains("partner_a")',
            run: "click",
        },
        {
            content: "Add items",
            trigger:
                'div[name="invoice_line_ids"] .o_field_x2many_list_row_add a:contains("Add a line")',
            run: "click",
        },
        {
            content: "Select product_a",
            trigger:
                'div[name="invoice_line_ids"] .o_selected_row .o_list_many2one[name="product_id"] input',
            run: "click",
        },
        {
            content: "Type product_a",
            trigger:
                'div[name="invoice_line_ids"] .o_selected_row .o_list_many2one[name="product_id"] input',
            run: "edit product_a",
        },
        {
            content: "Valid product_a",
            trigger: '.ui-menu-item-wrapper:contains("product_a")',
            run: "click",
        },
        {
            content: "Select analytic_distribution",
            trigger:
                'div[name="invoice_line_ids"] .o_selected_row .o_analytic_distribution_cell',
            run: "click",
        },

        {
            content: "Type Manual Distribution 1",
            trigger:
                'div[name="invoice_line_ids"] .o_selected_row .analytic_distribution_popup input[id="analytic_manual_distribution"]',
            run: "edit Manual Distribution 1",
        },
        {
            content: "Valid Manual Distribution 1",
            trigger:
                'div[name="invoice_line_ids"] .o_selected_row .analytic_distribution_popup li a:contains("Manual Distribution 1")',
            run: "click",
        },
        // The tour steps execute faster than the time it takes for JavaScript
        // to set the distribution. This can cause the distribution step to
        // not be fully completed before moving to the next step.
        // To address this, we introduce a 1-second delay (1000 milliseconds)
        // to give enough time for the distribution process to complete
        // before closing the popup.
        {
            content: "Wait 1 second before closing popup",
            trigger:
                'div[name="invoice_line_ids"] .o_selected_row .analytic_distribution_popup input[id="analytic_manual_distribution"]',
            run: () => new Promise((resolve) => browser.setTimeout(resolve, 1000)),
        },
        // Compatibility with analytic_distribution_widget_remove_save
        // this module remove buttons
        // so to close popup click on any form area
        {
            content: "Close Popup",
            trigger: "div.o_form_sheet_bg",
            run: "click",
        },
        // No action, just a check
        {
            content: "Check Tag Manual is on the top",
            trigger:
                'div[name="invoice_line_ids"] div.o_field_analytic_distribution[name="analytic_distribution"] div.o_field_tags div.o_tag_badge_text:contains("Manual Distribution 1")',
            run: () => null,
        },
        // Save account.move
        ...stepUtils.saveForm(),
        {
            content: "Confirm Invoice",
            trigger: 'button[name="action_post"]',
            run: "click",
        },
    ],
});
