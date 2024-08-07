/** @odoo-module */

import tour from "web_tour.tour";

tour.register(
    "account_analytic_distribution_manual",
    {
        test: true,
        url: "/web",
    },
    [
        tour.stepUtils.showAppsMenuItem(),
        {
            id: "account_menu_click",
            content: "Go to Invoicing",
            trigger: '.o_app[data-menu-xmlid="account.menu_finance"]',
        },
        {
            content: "Go to Customers",
            trigger: 'span:contains("Customers")',
        },
        {
            content: "Go to Invoices",
            trigger: 'a:contains("Invoices")',
        },
        {
            extra_trigger: '.breadcrumb:contains("Invoices")',
            content: "Create new invoice",
            trigger: ".o_list_button_add",
        },
        {
            content: "Add Customer",
            trigger:
                'div.o_field_widget.o_field_res_partner_many2one[name="partner_id"] div input',
            run: "text partner_a",
        },
        {
            content: "Valid Customer",
            trigger: '.ui-menu-item a:contains("partner_a")',
        },
        {
            content: "Add items",
            trigger:
                'div[name="invoice_line_ids"] .o_field_x2many_list_row_add a:contains("Add a line")',
        },
        {
            content: "Select product_a",
            trigger:
                'div[name="invoice_line_ids"] .o_selected_row .o_list_many2one[name="product_id"] input',
        },
        {
            content: "Type product_a",
            trigger:
                'div[name="invoice_line_ids"] .o_selected_row .o_list_many2one[name="product_id"] input',
            run: "text product_a",
        },
        {
            content: "Valid product_a",
            trigger: '.ui-menu-item-wrapper:contains("product_a")',
        },
        {
            content: "Select analytic_distribution",
            trigger:
                'div[name="invoice_line_ids"] .o_selected_row div.o_field_analytic_distribution[name="analytic_distribution"]',
        },
        {
            content: "Type Manual Distribution 1",
            trigger:
                'div[name="invoice_line_ids"] .o_selected_row .analytic_distribution_popup input[id="analytic_manual_distribution"]',
            run: "text Manual Distribution 1",
        },
        {
            content: "Valid Manual Distribution 1",
            trigger:
                'div[name="invoice_line_ids"] .o_selected_row .analytic_distribution_popup li a:contains("Manual Distribution 1")',
        },
        {
            content: "Apply selected Option",
            trigger:
                'div[name="invoice_line_ids"] .o_selected_row .analytic_distribution_popup input[id="analytic_manual_distribution"]',
            run: "click",
        },
        // Compatibility with analytic_distribution_widget_remove_save
        // this module remove buttons
        // so to close popup click on any form area
        {
            content: "Close Popup",
            trigger: "div.o_form_sheet_bg",
            run: "click",
        },
        {
            content: "Check Tag Manual is on the top",
            trigger:
                'div[name="invoice_line_ids"] .o_selected_row div.o_field_analytic_distribution[name="analytic_distribution"] div.o_field_tags div.o_tag_badge_text:contains("Manual Distribution 1")',
        },
        {
            content: "Confirm Invoice",
            trigger: 'button[name="action_post"]',
            run: "click",
        },
        // Save account.move
        ...tour.stepUtils.saveForm(),
    ]
);
