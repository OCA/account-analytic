# Copyright 2021 Open Source Integrators - Daniel Reis (www.opensourceintegrators.com)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    "name": "MO Procurement Group shared Analytic Account",
    "summary": "Analytic Account shared bty related Manufacturing Orders",
    "version": "14.0.1.0.0",
    "category": "Manufacturing",
    "author": "Open Source Integrators, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/account-analytic",
    "license": "AGPL-3",
    "depends": ["mrp_analytic"],
    "post_init_hook": "set_procurement_group_analytic_account",
    "installable": True,
}
