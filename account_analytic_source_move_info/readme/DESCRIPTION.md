This module adds source move information to analytic items:

- Analytic percentage used on the source journal item.
- Base amount of the source journal item.
- Base amount of the source journal entry.
- Percentage of the source journal entry base amount represented by the
  analytic item.

For invoices and receipts, the base amounts are taken from the untaxed
amounts. For other journal entries, the module uses the accounting
amounts available on the source journal item.

The values are stored on analytic items to make list views, exports and
reporting faster.
