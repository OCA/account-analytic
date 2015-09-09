# -*- coding: utf-8 -*-
# (c) 2015 Antiun Ingeniería S.L. - Pedro M. Baeza
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from openerp import models, api, exceptions, _


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    @api.multi
    def invoice_cost_create(self, data=None):
        invoice_model = self.env['account.invoice']
        invoice_line_model = self.env['account.invoice.line']
        analytic_line_model = self.env['account.analytic.line']
        invoices = []
        data = {} if data is None else data
        # use key (partner/account, company, currency)
        # creates one invoice per key
        invoice_grouping = {}
        # prepare for iteration on journal and accounts
        for line in self:
            key = (line.other_partner_id or line.account_id.partner_id,
                   line.account_id.company_id,
                   line.account_id.pricelist_id.currency_id)
            invoice_grouping.setdefault(key, []).append(line)
        for (partner, company, currency), analytic_lines in \
                invoice_grouping.items():
            account = analytic_lines[0].account_id
            if not partner or not currency:
                raise exceptions.Warning(
                    _('Contract incomplete. Please fill in the Customer and '
                      'Pricelist fields for %s.') % account.name)
            curr_invoice = self._prepare_cost_invoice(
                partner, company.id, currency.id, analytic_lines)
            invoice_context = dict(
                self.env.context, lang=partner.lang,
                # set force_company in context so the correct product
                # properties are selected (eg. income account)
                force_company=company.id,
                # set company_id in context, so the correct default journal
                # will be selected
                company_id=company.id)
            obj = invoice_model.with_context(invoice_context)
            last_invoice = obj.create(curr_invoice)
            invoices.append(last_invoice.id)
            # use key (product, uom, user, invoiceable, analytic account,
            # journal type) creates one invoice line per key
            invoice_lines_grouping = {}
            for analytic_line in analytic_lines:
                if not analytic_line.to_invoice:
                    raise exceptions.Warning(
                        _('Trying to invoice non invoiceable line for %s.') %
                        analytic_line.product_id.name)
                key = (analytic_line.product_id.id,
                       analytic_line.product_uom_id.id,
                       analytic_line.user_id.id,
                       analytic_line.to_invoice.id,
                       analytic_line.account_id,
                       analytic_line.journal_id.type)
                # We want to retrieve the data in the partner language for
                # the invoice creation
                obj = analytic_line_model.with_context(invoice_context)
                invoice_lines_grouping.setdefault(key, []).append(
                    obj.browse(analytic_line.id))
            # finally creates the invoice lines
            for ((product_id, uom, user_id, factor_id, account, journal_type),
                    lines_to_invoice) in invoice_lines_grouping.items():
                obj = self.with_context(invoice_context)
                invoice_line_vals = obj._prepare_cost_invoice_line(
                    last_invoice.id, product_id, uom, user_id, factor_id,
                    account, lines_to_invoice, journal_type, data)
                invoice_line_model.create(invoice_line_vals)
            analytic_lines = analytic_line_model.browse(
                [l.id for l in analytic_lines])
            analytic_lines.write({'invoice_id': last_invoice.id})
            last_invoice.button_reset_taxes()
        return invoices
