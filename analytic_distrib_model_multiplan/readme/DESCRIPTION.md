Populate default Analytic Distribution from multiple Analytic Distribution Models
providing the default value for different Analytic Plans.

A typical use case is Plan 1 - Territory gets a default value from the Partner,
and Plan 2 - Product Line gets a default value based on the Product.

Standard Odoo is unable to do this, as it will pick the first matching Analytic
Distribution Model, that will either propulate Plan 1 or Plan 2, but not both.
