* Add `account_analytic_id` in `pos.order` so we can use it in reports.
* In `13.0` the session reconciliation has been refactored and thus the journal
  items are now very simplified. There's no product detail now, so we won't
  be able to analyze that level of detail anymore. For invoices it remains as it
  was.
