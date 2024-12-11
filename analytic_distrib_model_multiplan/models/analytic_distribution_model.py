# Copyright (C) 2024 Open Source Integrators (https://www.opensourceintegrators.com)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
from odoo import api, models


class AccountAnalyticDistributionModel(models.Model):
    _inherit = "account.analytic.distribution.model"

    @api.model
    def _get_used_plans(self, analytic_distribution):
        "Returns the Plans used in an Analytic Distribution dict"
        Analytic = self.env["account.analytic.account"]
        analytic_ids = list((analytic_distribution or {}).keys())
        return Analytic.search([("id", "in", analytic_ids)]).plan_id

    @api.model
    def _get_distribution_exclude_plans(self, vals, exclude=None):
        """
        Same as standard _get_distribution, but can ignore Distribution Models
        using particular Plans.
        This allows to select and join further Distribution Models
        into a combined distribution.

        """
        domain = []
        for fname, value in vals.items():
            domain += self._create_domain(fname, value) or []
        best_score = 0
        res = {}
        fnames = set(self._get_fields_to_check())
        candidates = self.search(domain).filtered(
            lambda x: self._get_used_plans(x.analytic_distribution) not in exclude
        )
        for rec in candidates:
            try:
                score = sum(rec._check_score(key, vals.get(key)) for key in fnames)
            except:  # noqa
                score = 0
            if score > best_score and rec.analytic_distribution:
                res = rec.analytic_distribution
                best_score = score
        return res

    @api.model
    def _get_distribution(self, vals):
        res = super()._get_distribution(vals)
        # Find additional distribution models for unset Analytic Plans
        while True:
            plans = self._get_used_plans(res)
            res_add = self._get_distribution_exclude_plans(vals, exclude=plans)
            if not res_add:
                break
            res.update(res_add)
        return res
