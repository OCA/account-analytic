For each analytic account, defines the root analytic account, i.e. the parent account the most high up in the hierarchy. If there is no parent account, the root account is the account itself.

This module is useful for analytic reporting (via bi_view_editor for instance) of accounts organized in hierarchy. 

The parent account cannot be used for reporting if there is more or less than two hierarchical layers, and if the parent accounts are used directly as account in the analytic lines. 

Having root parent analytic account enable aggregate reporting for hierarchy of accounts that is not 

For instance, let's assume we have a analytic account hierarchy like:

- Account A / Account AB / Account ABC
- Account B
- Account C / Account CB

If we group by parent analytic account we get:

- Account A 
- Account A / Account AB 
- Account C
- no value


If we group by root analytic account we get:

- Account A
- Account B
- Account C

Which is much cleaner.
