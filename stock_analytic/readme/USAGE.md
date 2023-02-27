## To Assign an Analytic Account to a Stock Move

You need to:

1.  Create manually or open draft picking
2.  Add move lines and assign an **analytic account** in Analytic
    Distribution field

## Assigned Journal Items created from Stock Move with Analytic Account

If stock move automatically create journal entry, the journal entry will
contain journal items with following rule:

1.  Journal item with account equal to product's valuation account will
    not be assigned to any analytic account.
2.  Journal item with account different to product's valuation account
    will be assigned to an analytic account according to the stock
    move's analytic account.

## Analytic applicability judgment

Applicability of the analytic distribution is judged based on the applicability
settings of the analytic plan.

Note that this module adds the 'Stock Move' option to the business domain, and
'Operation Type' field.

Return moves are currently outside the scope of the validation / applicability judgment
(i.e. treated the same as optional) to allow some flexibility in the operation since
multiple factors (e.g. applicability of the original move) may need to be considered
to correctly judge the applicability.
