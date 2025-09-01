This module extends the stock and analytic accounting capabilities by automatically creating analytic lines from stock based on configurable rules.

Key features:

- Define stock movement rules by source and destination locations.
- Compute analytic line amounts using either:
  - Product list price.
  - Category-based formula: `(avg_price * (avg_weight * qty)) + ((avg_weight * qty) * supplement)`
- Support for positive and negative analytic distributions.
- Handles partial distributions and multi-account combinations.
- Supports return pickings and reversal analytic lines.
- Fully compatible with analytic plans and multidimensional analytic accounting.

The module is useful for organizations needing precise analytic accounting for inventory movements, such as manufacturing, logistics, or services.
