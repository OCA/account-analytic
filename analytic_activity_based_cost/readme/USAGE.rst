When creating Analytic Items, if a configuration is in place, the corresponding Analytic Items for indirect cost are generated.

* When an Analytic Item is created, an automatic process checks the Activity Based Cost Rules to identify the ones that apply.
* Each triggered rule created a new Analytic Item, with a copy of the original one, and:
    * Product: is the rule Cost Type Product. A validation error prevents this from being the same as the source Analytic Item Product, to avoid infinite loops.
    * Quantity: is the original quantity multiplied by the rule's Factor
    * Amount: is -1 * Quantity * Product Standard Price
    * Parent Analytic Item (new field): set with the original Analytic Item
* An update on the Quantity triggers a recalculation of the quantity and amount of the child Analytic Items.
* A delete cascades to the child Analytic Items, causing them to also be deleted.
