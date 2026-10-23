# Copyright 2026 - TODAY, Kaynnan Lemes <kaynnan.lemes@escodoo.com.br>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models


class PurchaseBlanketOrderLine(models.Model):
    _name = "purchase.blanket.order.line"
    _inherit = ["purchase.blanket.order.line", "analytic.mixin"]
