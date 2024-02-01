# Copyright 2014 Acsone - Stéphane Bidoul <stephane.bidoul@acsone.eu>
# Copyright 2017 Tecnativa - Vicent Cubells <vicent.cubells@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, exceptions, fields, models


class AccountAccountType(models.Model):
    _inherit = "account.account.type"

    property_analytic_policy = fields.Selection(
        selection_add=[
            ('always_plan', 'Always (analytic distribution)'),
            ('always_plan_or_account',
             'Always (analytic account or distribution)')
        ],
    )


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    @api.multi
    def _check_analytic_distribution_required_msg(self):
        for move_line in self:
            analytic_distribution = move_line.analytic_tag_ids.filtered(
                "active_analytic_distribution")
            if move_line.analytic_account_id and analytic_distribution:
                return _('Analytic account and analytic distribution '
                         'are mutually exclusive')
            if move_line.debit == 0 and move_line.credit == 0:
                continue
            analytic_policy = self._get_analytic_policy(move_line.account_id)
            if analytic_policy == 'always_plan' and not analytic_distribution:
                return _("Analytic policy is set to "
                         "'Always (analytic distribution)' with account "
                         "%s '%s' but the analytic distribution is "
                         "missing in the account move line with "
                         "label '%s'.") % \
                        (move_line.account_id.code,
                         move_line.account_id.name,
                         move_line.name)
            if analytic_policy == 'always_plan_or_account' \
                    and not move_line.analytic_account_id \
                    and not analytic_distribution:
                return _("Analytic policy is set to "
                         "'Always (analytic account or distribution)' "
                         "with account %s '%s' but the analytic "
                         "distribution and the analytic account are "
                         "missing in the account move line "
                         "with label '%s'.") % \
                        (move_line.account_id.code,
                         move_line.account_id.name,
                         move_line.name)
            elif analytic_policy == 'never' and analytic_distribution:
                return _("Analytic policy is set to 'Never' with account "
                         "%s '%s' but the account move line with label "
                         "'%s' has an analytic distribution %s '%s'.") % \
                        (move_line.account_id.code,
                         move_line.account_id.name,
                         move_line.name,
                         move_line.analytic_account_id.code,
                         move_line.analytic_account_id.name)

    @api.constrains('analytic_account_id', 'analytic_tag_ids',
                    'account_id', 'debit', 'credit')
    def _check_analytic_required(self):
        for rec in self:
            message = rec._check_analytic_distribution_required_msg()
            if message:
                raise exceptions.ValidationError(message)
            else:
                super(AccountMoveLine, self)._check_analytic_required()
