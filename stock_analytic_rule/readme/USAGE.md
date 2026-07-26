1. Configure Product Categories

Navigate to **Inventory > Configuration > Product Categories**.

For each relevant product category, configure the following fields:

- `Average Price`: Base cost per unit.
- `Average Weight`: Used to scale the cost relative to quantity.
- `Supplement`: Additional surcharge applied on top of base cost.

### Custom Computation for Internal Moves

If **Custom Computation for Internal Moves** is enabled, specific values can be defined for internal transfers.

When this option is checked, the following fields appear:

- **Average Price for Internal Moves**
- **Average Weight for Internal Moves**

These values will be used **instead of** **Average Price** and **Average Weight** when calculating the total amount for internal stock moves.

These values are used when the compute type is set to **Category**.

---

2. Define Analytic Accounts and Plans

Navigate to **Accounting > Configuration > Analytic Accounting**.

- Create one or more **Analytic Plans**.
- Create **Analytic Accounts** linked to these plans.

These accounts will be referenced in the analytic distribution logic of each model.

---

3. Create Stock Analytic Rules

Navigate to **Accounting > Configuration > Stock Analytic Rules**.

Configure each rule with:

- `Name`: Used as the label for the generated analytic lines.
- `Source Locations` and `Destination Locations`: Determines when the model applies.
- `Amount Compute Type`: Choose between:
  - **Product** – uses the product's list price.
  - **Category** – uses the category's formula `(avg_price × weight × qty) + (weight × qty × supplement)`.
- `Analytic Distribution` (for positive lines)
- `Negative Analytic Distribution` (for negative lines)
- `Financial Account`: Used in the generated analytic line.

📌 **Note**: The distribution for reversed moves (e.g. returns) is automatically computed by inverting the accounts — no need to define a separate rule.

4. Perform a Stock Move

Create a Transfer that matches the configured rule:

- It can be internal, delivery, or receipt.

- Ensure the source and destination locations match the analytic rule.

5. Review Analytic Lines

Navigate to Accounting > Accounting > Analytic Lines.

You should now see the automatically generated analytic lines reflecting the cost and distribution defined in your model.
