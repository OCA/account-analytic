This module adds the ability to set a default analytic account on
accounts.

You can define multiple search conditions for one analytical account by using
different parameters. All parameters are equal, and in search result you will
get analytical account with best match index.
Thus you should be careful when you want define for instance specific
conditions for partner. You should define all default accounts for this partner
+ account_id, as each move have required account_id and it sent in background.

Example:

default_account_1  settings ->  account_id = sale_account
default_account_2  settings ->  partner_id = partner_1

For this settings default_account_2 will be never returned for accounting sale
entry, as it will be beaten by default_account_1

For correct search setting should be:

default_account_2 setup settings ->   account_id = sale_account
                                 and  partner_id = partner_1
