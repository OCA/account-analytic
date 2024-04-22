# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class StockRule(models.Model):
    _inherit = "stock.rule"

    def _make_po_get_domain(self, company_id, values, partner):
        """
        If a procurement has an analytic distribution, it should go with lines
        whose distributions fully contain the accounts of its distribution.
        """
        res = super()._make_po_get_domain(company_id, values, partner)
        proc_distribution = values.get("analytic_distribution", False)
        if not proc_distribution:
            domain_addendum = (
                ("order_line.analytic_distribution", "=", proc_distribution),
            )
        else:
            # Compromise: the analytic_distribution field does not allow us to
            # check for strict equality that includes the distribution weights
            # (the values of the dictionary). So we compromise by saying if we
            # find an order that has a line that contains all of the accounts of
            # the distribution, it is OK for our procured line to go on that
            # order. If there are differences in the exact distribution, the
            # _find_candidate method on purchase.order.line will reject them, so
            # we will create a new line as necessary. Thus lines with
            # distributions {"1": 100, "2": 100, "3": 100} and {"1": 70, "2":
            # 30} may end up on the same PO, but will still get their own lines.
            # Odoo also does not allow us to check for full containment ("in"
            # only checks for any intersection, so {"1": 100, "2": 100} is "in"
            # {"2": 70, "3": 30}.
            # So we break the check apart into multiple "in" leaves: if each
            # separate account is "in" a distribution, that means the entire set
            # of accounts is as well
            domain_addendum = tuple(
                ("order_line.analytic_distribution", "in", (analytic,))
                for analytic in proc_distribution.keys()
            )

        res += domain_addendum
        return res

    def _get_procurements_to_merge_groupby(self, procurement):
        """
        Do not merge procurements with different analytic distributions
        """
        res = super()._get_procurements_to_merge_groupby(procurement)
        distribution = procurement.values.get("analytic_distribution")
        if not distribution:
            prefix = ((False, False),)
        else:
            prefix = tuple(sorted(distribution.items()))
        return prefix + res
