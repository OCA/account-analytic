The module works automatically:

1. Create a sale order
2. Add products to order lines
3. The system automatically applies analytic distribution based on the order warehouse
4. Confirm the order

The analytic distribution appears in the **Analytic Distribution** field on each sale order line.

**Note:** Manual changes to the analytic distribution field are still possible if needed.

**Note:** Changing the warehouse of the order may recompute the analytic distribution of all its lines. If the new warehouse has a distribution model, its result replaces the value of every line, manual values included. If it has none, the lines keep the distribution they already had.