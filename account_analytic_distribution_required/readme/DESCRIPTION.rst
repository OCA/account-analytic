This module extends account_analytic_required and adds 2 policies to
control the use of analytic distributions. The policies behave as follow

* never: no analytic account nor analytic distribution allowed
* always: analytic account required
* always_plan: analytic_distribution required
* always_plan_or_account: analytic distribution or analytic account required
* optional: do what you like,

In any case analytic account and analytic distribution are mutually exclusive.
