This module allows you to configure **income analytic account/tags** and
**expense analytic account/tags** on products and on product categories. When you
select the product in an invoice line, it will check if this product has an
income analytic account (for customer invoice/refunds) or an expense analytic
account (for supplier invoice/refunds) ; if it doesn't find any, it checks if
the category of the product has an income or expense analytic account ; if an
analytic account is found, it will be set by default on the invoice line.
For analytic tags, it will return the **union** of tags found at product and
category level.
