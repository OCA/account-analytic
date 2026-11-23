User friendly import of Analytic Distribution in Journal Items.

This module is an alternative to ``account_analytic_distribution_manual``
for import purposes: that module provides named, reusable analytic
distributions and an importable JSON field using analytic account names,
on any model using ``analytic.mixin``. This module only targets journal
items and offers dedicated, non-stored columns, which makes column mapping
in CSV/Excel files straightforward, at the cost of flexibility (fixed
positions, single distribution set to 100%).
