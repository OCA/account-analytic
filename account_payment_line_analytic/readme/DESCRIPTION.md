This is a glue module, automatically installed when both
`account_analytic_payment` and `account_payment_line` are installed.

It propagates the analytic distribution set on the payment header to its
counterpart lines: a counterpart line that has no analytic distribution
inherits the one from the payment, while a line that already has its own
distribution keeps it.
