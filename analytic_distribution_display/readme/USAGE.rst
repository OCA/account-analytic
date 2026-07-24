#. Open the Export wizard on any model that has an analytic distribution
   (e.g. Purchase Order Lines, Invoice Lines, Sale Order Lines, Expenses).
#. Look for the field **Analytic Distribution (text)** and add it to the
   list of fields to export.
#. Export the file: the column will contain the analytic account names and
   percentages (e.g. ``Obra 218 (60.00%) | Administrativo (40.00%)``)
   instead of the raw JSON stored in ``analytic_distribution``.
#. The same field can be used in QWeb or ``report_xlsx`` reports.
