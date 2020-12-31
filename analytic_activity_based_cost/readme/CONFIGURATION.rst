Create the Products representing the Cost Types to use:

    * Go to Invoicing/Accounting > ... > Products, and create Products representing the Cost Types to use. Set the standard cost to use for each unit used.

Configure the Activity Based Cost Rules, setting the triggers to generate the cost Analytic Items:

    * Go to Invoicing/Accounting > Configuration > Activity Based Cost Rules.
    * Create a new rule:
        * Name: a descriptive title, required
        * Start Date: an optional application start date
        * End Date: an optional application end date
        * Activity Product: the Analytic Item Product generating costs, if given. Optional.
        * Must have related Project: check to only apply if the Analytic Item is related to a Project. Allows to identify timesheet generated Analytic Items.
        * Factor: a quantity multiplier to calculate the cost type quantity. Defaults to 1.
        * Cost Type Product: a Product that represents the cost type to assign, such as "Overhead". The Product's standard cost will be used to calculate amounts.
