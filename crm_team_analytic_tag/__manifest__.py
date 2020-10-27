# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Crm Team Analytic Tag",
    "summary": """
        This addon add analytic tags to sale teams to be added to invoice lines
        when the team is selected in the invoice level""",
    "version": "12.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV,"
              "Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/account-analytic",
    "depends": ["sale"],
    "data": ["views/crm_team.xml"],
}
