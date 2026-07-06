This module reintroduces the hierarchy to the analytic accounts as it
was in previous versions of Odoo. This module is a base module for other
modules to manage the hierarchy concept in analytics.

It also exposes a computed **Level** field expressing the depth of each
account within its subtree: level 0 for a leaf account (no children), level
1 for a parent whose children are all leaves, level 2 for a grandparent...
