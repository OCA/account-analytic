This module adds a many2many analytic accounts field, which is computed based on the
value of analytic distribution, to the analytic mixin in a bid to overcome the
inconveniences of not having them directly on the model that inherits the mixin.

Possible use cases:

* Include analytic accounts field in data export.
* Use the field as a hook point to add some logic in a custom module.

The module also adds a field for analytic account names, which displays the names of
these accounts in a comma-separated format. This feature could be useful for efficient
data administration as applicable (e.g. you do not want to split lines per analytic
account when records are exported).
