#  Copyright (c) 2025 Groupe Voltaire
#  @author Guillaume MASSON <guillaume.masson@groupevoltaire.com>
#  License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Analytic Distribution per Sales Team",
    "summary": """
        Adds "Sales Team" as a criteria for analytic distribution models.
    """,
    "version": "16.0.1.0.0",
    "author": "Groupe Voltaire, Akretion, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/account-analytic",
    "category": "Analytic Accounting",
    "depends": ["analytic", "sale", "sales_team"],
    "data": [
        "views/account_analytic_distribution_model_views.xml",
    ],
    "maintainers": ["metaminux"],
    "installable": True,
    "application": False,
    "auto_install": False,
    "license": "AGPL-3",
}
