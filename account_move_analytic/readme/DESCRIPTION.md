This module adds analytic distribution support at the invoice and vendor bill
level.

**Features:**

- Adds an analytic distribution field on the invoice/bill header (form and list views)
- When you set an analytic distribution on the header, it is automatically
  propagated to all invoice lines (sections and notes are excluded)
- If all invoice lines share the same analytic distribution, it is displayed
  on the header; otherwise, the header field remains empty
- New invoice lines automatically inherit the header's analytic distribution

This functionality only applies to customer invoices, customer credit notes,
vendor bills, and vendor credit notes. Journal entries are not affected.
