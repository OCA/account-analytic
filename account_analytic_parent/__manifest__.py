# Copyright 2017 ForgeFlow S.L.
# Copyright 2017 Luxim d.o.o.
# Copyright 2017 Matmoz d.o.o.
# Copyright 2017 Deneroteam.
# Copyright 2017 Serpent Consulting Services Pvt. Ltd.
# Copyright 2017 Tecnativa
# Copyright 2018 Brainbean Apps
# Copyright 2020 CorporateHub (https://corporatehub.eu)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "Account Analytic Parent",
    "summary": """
        This module reintroduces the hierarchy to the analytic accounts.""",
    "version": "14.0.1.0.1",
    "license": "AGPL-3",
    "author": "Matmoz d.o.o., "
    "Luxim d.o.o., "
    "Deneroteam, "
    "ForgeFlow, "
    "Tecnativa, "
    "CorporateHub, "
    "Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/account-analytic",
    "depends": ["account", "analytic"],
    "data": ["views/account_analytic_account_view.xml"],
    "demo": ["data/analytic_account_demo.xml"],
    "post_init_hook": "post_init_hook",
}
