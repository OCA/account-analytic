This module defines **cross-plan analytic account mappings**. When an analytic
account is used in an analytic distribution, the accounts it's mapped to are
added automatically to the same distribution line (on its own analytic plan).

Rules enforced on the mapped accounts:

- A source account can map to at most one account per destination plan.
- A mapped account must belong to different root plan than the source account.
- Mappings are applied directly (no transitive chaining).

Because the mapping lives on the analytic account itself, it follows the
account's company: a company-specific account can only be mapped to accounts of
the same company or shared accounts, and a shared account can only be mapped to
shared accounts. This is enforced automatically.
