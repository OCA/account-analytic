This module extends the stock and analytic accounting capabilities by automatically creating analytic lines from stock based on configurable rules.

Key features:

- Define stock movement rules by source and destination locations.
- Compute analytic line amounts using either:
  - Product list price.
  - Category-based formula:
    - For products measured in units, total_weight is calculated as quantity * weight.
    - The product's weight is used when available; otherwise, the category's average weight (avg_weight) is used.
    - For products measured in weight units (kg, grams, tonnes, etc.), the quantity is automatically converted to kilograms, avoiding double weight calculations.
- Support for positive and negative analytic distributions.
- Handles partial distributions and multi-account combinations.
- Supports return pickings and reversal analytic lines.
- Fully compatible with analytic plans and multidimensional analytic accounting.

The module is useful for organizations needing precise analytic accounting for inventory movements, such as manufacturing, logistics, or services.
