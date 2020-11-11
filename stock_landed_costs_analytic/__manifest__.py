# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Stock Landed Costs Analytic",
    "summary": """
        This module adds an analytic account and analytic tags on landed costs
        lines so that on landed costs validation account moves get analytic
        account and analytic tags values from landed costs lines.""",
    "version": "13.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/account-analytic",
    "depends": ["stock_landed_costs"],
    "data": ["views/stock_landed_cost_lines.xml"],
    "demo": [],
}
