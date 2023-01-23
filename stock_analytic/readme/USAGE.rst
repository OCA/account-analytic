To Assign an Analytic Account to a Stock Move
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You need to:

#. Create manually or open draft picking
#. Add move lines and assign an **analytic account** in Analytic Distribution field

Assigned Journal Items created from Stock Move with Analytic Account
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If stock move automatically create journal entry, the journal entry will
contain journal items with following rule:

#. Journal item with account equal to product's valuation account will not be
   assigned to any analytic account.
#. Journal item with account different to product's valuation account will be
   assigned to an analytic account according to the stock move's analytic
   account.
