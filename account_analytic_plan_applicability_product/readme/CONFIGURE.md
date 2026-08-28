To configure this module, you need to:

1.  Go to an analytic plan
2.  Select the product(s) you want to use to restrict the applicability
    of this plan

Note that the behavior can be non-intuitive when having applicability lines with products with a category being used in other applicability lines. Ie

| Product category | Product        | Applicability|
|------------------|----------------|--------------|
| cat1             |                | optional     |
|                  | prod-with-cat1 | mandatory    |

will leave you with applicability optional when product-with-cat1 is used. Do

| Product category | Product        | Applicability|
|------------------|----------------|--------------|
| cat1             |                | optional     |
| cat1             | prod-with-cat1 | mandatory    |

if you want to make the plan mandatory in that case. If you use multiple products with different categories, and you also use those categories separately for applicability, you'll have to split the applicability lines by category, as in

| Product category | Product        | Applicability|
|------------------|----------------|--------------|
| cat1             |                | optional     |
| cat1             | prod-with-cat1 | mandatory    |
| cat2             |                | unavailable  |
| cat2             | prod-with-cat2 | mandatory    |
