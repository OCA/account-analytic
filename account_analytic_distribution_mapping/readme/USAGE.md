1.  Go to *Invoicing > Configuration > Analytic Accounting > Analytic
    Accounts* and open the account you want to map.
2.  In the *Analytic Mapping* tab, add the accounts it should pull in under
    **Mapped Accounts**. Each must belong to a different analytic plan than the
    account itself and other mapped accounts.
3.  On any document with analytic distribution, select the source account. The
    mapped account(s) are added automatically on their own plan.

To write a distribution without applying the mappings, set the context key
`skip_analytic_distribution_mapping=True`.
