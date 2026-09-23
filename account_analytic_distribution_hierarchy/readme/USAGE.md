# Usage

## For End Users

No special configuration is needed. Simply use Odoo's analytic distribution
widget as usual:

1. Create a Sale Order, Purchase Order, or Journal Entry
2. Select a **child analytic account** (e.g., "Work Order A of Project XY")
3. The system automatically adds the **parent account** (e.g., "Project XY")
   to the distribution
4. Both accounts will be visible in the analytic distribution JSON

## For Reporting with MIS Builder

This module is specifically designed to work with the OCA **mis_builder**
module for hierarchical reporting.

### Report on Child Accounts (Work Order Level)

Create a MIS Report filter for a specific work order:

```
Analytic Account = "Work Order A of Project XY"
```

This shows only the costs/revenue for that specific work order.

### Consolidate on Parent Accounts (Project Level)

Create a MIS Report filter for the parent project:

```
Analytic Account = "Project XY"
```

This shows ALL costs/revenue from all work orders under that project,
enabling project-level budgeting and reporting.

### Budget vs Actual Example

1. Set budgets at the **parent level** (Project XY)
2. Track actuals at the **child level** (Work Order A, B, C)
3. Run MIS Reports comparing budget (parent) vs actuals (parent) to see
   overall project performance
4. Drill down by filtering on child accounts to see which work orders are
   over/under budget

## Technical Note

The module hooks into the `create()` and `write()` methods of all models
inheriting `analytic.mixin`. When an `analytic_distribution` dictionary is
saved, it:

1. Scans all account IDs in the JSON
2. Checks if any account has a `parent_id`
3. If yes and the parent is not already in the JSON, injects it with the
   same percentage as the child
