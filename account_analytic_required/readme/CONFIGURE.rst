Example:

If you want to have an analytic account on all your *expenses*,
set the policy to *always* for the account of type *expense*.
If you try to save a journal items with an account of type *expense*
without analytic account, you will get an error message.

If you also want the distribution to be complete, tick *Require full analytic
distribution* on the account. It applies on top of the *always* and *posted
moves* policies, and is checked per analytic plan: a line split between a
department plan and a project plan legitimately adds up to 200%, while each
plan on its own has to cover the full amount.

Odoo does have a native 100% check, but it only covers plans configured as
*mandatory* through the analytic applicability rules, and it only runs when
the request carries the ``validate_analytic`` context, which the posting
buttons set. Posting from code, from a cron, from an import or over RPC skips
it. The check added here is a model constraint, so it applies on every write
whatever the origin, and it is configured per account rather than per plan.
