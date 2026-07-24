* Add a ``store=True`` variant so the field can be used to group, filter and
  sort in list views. This requires invalidating/recomputing the field when
  ``account.analytic.account.name`` changes, which is left out of this first
  version for simplicity.
* Add the field to the native list views of specific apps (purchase, sale,
  account, hr_expense, ...) through dedicated glue modules, e.g.
  ``purchase_analytic_distribution_display``.
* Support using this field in ``search()`` domains.
