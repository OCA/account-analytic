1. **Navigate to Analytic Distribution Models**

- Go to Invoicing -> Configuration -> Analytic Distribution Models.

2. **Create or Edit a Distribution Model**

- Create a new distribution model or edit an existing one.
- Set the **Start Date** and **End Date** to define the active period for the distribution. Only distributions within this date range will be applied.
- Define filters such as **Partner** and **Account Prefix** to control when the model should apply.

3. **Create an Invoice or Vendor Bill**

- Select a customer and an account that match the conditions set in the distribution model.
- If the invoice has a date, the system will use it to filter applicable distribution models; otherwise, it will use the current date.

4. **Use the Recalculate Function**

- Go to **Analytic Distribution Models**.
- Enable the **Recalculate** option on the model you want to update.
- Modify the analytic distribution as needed.
- Click the **Recalculate** button. (Partner and account prefix needs to be set)
- All journal items originally updated using this model, and still within its date range and matching its criteria, will be recalculated, using the current distribution of the model.
