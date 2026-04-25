# Analytic Distribution Hierarchy

This module extends the OCA `account_analytic_parent` module to enable
hierarchical analytic reporting with Odoo 18's `analytic_distribution` JSON
field.

## Business Context

In engineering and project-based companies, you often need to track costs at
two levels simultaneously:

1. **Project/Customer Level** (Parent Account) - for budgeting and consolidated
   reporting
2. **Work Order/Equipment Level** (Child Account) - for operational tracking

**Example:**
- Parent Account: "Project XY" (Customer level)
- Child Account: "Work Order A of Project XY" (Equipment level)

## How It Works

When a user selects a **child analytic account** in the analytic distribution
widget, this module automatically injects the **parent account** into the same
distribution with the same percentage.

**Before (user input):**
```json
{"1234": 100}
```

**After (automatic injection):**
```json
{"1234": 100, "5678": 100}
```

Where:
- `1234` = Work Order A (child)
- `5678` = Project XY (parent)

## How this Works with MIS Builder

The OCA **mis_builder** module queries `account.move.line` directly and checks
if an analytic account ID exists in the `analytic_distribution` JSON keys. It
then sums the journal item balance directly **without multiplying by the
percentage**.

This means:
- Filtering by **child account** shows only that work order's costs
- Filtering by **parent account** shows ALL costs from all its children
- No double-counting occurs because MIS Builder uses the full AML balance

## Key Features

- **Automatic parent injection** on create and write operations
- **Works on all models** using `analytic.mixin` (Sale Orders, Purchase Orders,
  Journal Entries, etc.)
- **Zero user training required** - works transparently in the background
- **Perfect for project-based budgeting** with MIS Builder
