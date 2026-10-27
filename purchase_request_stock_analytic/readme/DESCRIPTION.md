When a buy rule creates a purchase request line, this module copies on the line
the analytic distribution of the stock move at the origin of the need (set by
*Stock Analytic*, for instance from a manufacturing order). The purchase order
created from the purchase request then keeps the analytic distribution of each
line.

A purchase request line is created for each need, so two needs with different
analytic distributions give two lines. A need without analytic distribution
gives a line without analytic distribution.
