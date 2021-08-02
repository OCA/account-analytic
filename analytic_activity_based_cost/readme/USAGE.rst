When creating Analytic Items for a cost driver Product,
the corresponding Analytic Items for driven cost are generated.

* When an Analytic Item is created, an automatic process
  checks the Activity Based Cost Rules to identify the ones that apply.
* Each rule creates a new Analytic Item for the driven costs,
  as a copy of the original one, with:

    * Product: set to rule's Cost Type Product.
      A validation error prevents this from being
      the same as the source Analytic Item Product, to avoid infinite loops.
    * Cost Quantity: is the original quantity multiplied by the rule's Factor
    * Cost Amount: is -1 * Quantity * Product Unit  Cost
    * Parent Analytic Item (new field): set with a link to the original Analytic Item
    * Quantity: zero, to avoid duplication
    * Amount: zero, to avoid duplication
    * Project and Task: if present, are reset, to avoid representing the driven costs
      as timesheet lines.

An update on the original Quantity triggers a recalculation of the quantity and amount of the child Analytic Items.

A delete cascades to the child Analytic Items, causing them to also be deleted.
