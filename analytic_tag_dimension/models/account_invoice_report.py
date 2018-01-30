# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class AccountInvoiceReport(models.Model):
    _inherit = "account.invoice.report"

    def _get_dimension_fields(self):
        return [x for x in self.fields_get().keys()
                if x.startswith("x_dimension_")]

    def _select(self):
        res = super()._select()
        add_fields = self._get_dimension_fields()
        add_fields = [", sub.{0} as {0}".format(x) for x in add_fields]
        return res + "".join(add_fields)

    def _sub_select(self):
        res = super()._sub_select()
        add_fields = self._get_dimension_fields()
        add_fields = [", ail.{0} as {0}".format(x) for x in add_fields]
        return res + "".join(add_fields)
