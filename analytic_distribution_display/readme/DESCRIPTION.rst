Since Odoo 16.0, the analytic distribution of documents (purchase order
lines, invoice lines, sale order lines, expenses, ...) is stored as a JSON
field mapping analytic account ids to percentages, e.g. ``{"218": 100.0}``.

Turning that JSON into a readable label is only handled by the web widget,
so anything that bypasses the widget - exports to XLSX/CSV, QWeb reports,
``report_xlsx`` - shows the raw JSON with numeric ids instead of the
account names.

This module adds a computed, human readable ``analytic_distribution_display``
field to every model inheriting the ``analytic.mixin`` abstract model, so it
can be used in exports and reports.
