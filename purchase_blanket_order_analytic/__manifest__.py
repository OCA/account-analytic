# Copyright 2026 Escodoo (https://escodoo.com.br)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


{
    "name": "Purchase Blanket Order Analytic",
    "version": "16.0.1.0.0",
    "author": "Escodoo, Odoo Community Association (OCA)",
    "category": "Purchase Management",
    "website": "https://github.com/OCA/account-analytic",
    "depends": ["purchase_blanket_order", "base_view_inheritance_extension"],
    "data": [
        "security/ir.model.access.csv",
        "views/purchase_blanket_order_views.xml",
    ],
    "license": "AGPL-3",
    "installable": True,
    "application": False,
}
