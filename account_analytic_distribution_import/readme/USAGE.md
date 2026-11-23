On file import, four additional columns are available for Analytic 1, Analytic 2, etc.
These helper columns provide an easy way to load an Analytic Distribution.

The helper columns are not stored: they only carry the imported values and are
translated into ``analytic_distribution`` when the journal items are created
or updated. The provided accounts are combined, in column order, into a
single analytic distribution set to 100%.

When updating existing journal items, the columns that are filled define the
complete analytic distribution of the line; an explicit ``Analytic
Distribution`` value in the import file takes precedence over them.
