This module allows you to configure an **income analytic account/tag** and an
**expense analytic account/tag** on products and on product categories. When you
select the product in an invoice line, it will check if this product has an
income analytic account/tag (for customer invoice/refunds) or an expense analytic
account/tag (for supplier invoice/refunds) ; if it doesn't find any, it checks if
the category of the product (or the nearest parent category) has an income or
expense analytic account/tag ; if an analytic account/tag is found, it will be
set by default on the invoice line.
