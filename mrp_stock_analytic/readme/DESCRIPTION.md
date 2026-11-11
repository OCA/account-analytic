Allows to assign the analytic distribution in the manufacturing order,
which propagates the value to the component stock moves. Optionally,
it can also propagate to finished product moves (including byproducts)
when the corresponding setting is enabled.

This function can be useful when cost analysis needs to be done on
consumed components or finished products.

Additionally, analytic distribution from manufacturing orders is propagated
to WIP accounting entries. When creating WIP journal entries through the WIP
Accounting wizard, the analytic distribution is automatically applied to the
WIP account move lines. When multiple manufacturing orders with different
analytic distributions are selected, separate WIP lines are created for
each analytic distribution.

This module depends on OCA module stock_analytic.
