# -*- coding: utf-8 -*-
# © 2017 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp import _, api, models
from openerp.exceptions import ValidationError


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    @api.constrains('analytic_journal_id', 'company_id')
    def _check_analytic_journal_id(self):
        """Journal and analytic journal should be in same company."""
        for this in self:
            if this.analytic_journal_id and \
                    this.company_id != this.analytic_journal_id.company_id:
                raise ValidationError(_(
                    "Journal and analytic journal must belong to the same"
                    " company.\n"
                    "Analytic journal belongs to company %s.") %
                    this.analytic_journal_id.company_id.name
                )
