To define related accounts (used by the filter)

1.  Go to *Invoicing → Configuration → Analytic Distribution
    Accounts*.
2.  Open the analytic account and add its related accounts in the
    **Related Accounts** table.
    - If no related accounts are set, the widget falls back to standard
      (unfiltered) behavior.

## Example

You have three plans, each with two accounts:

- **Plan 1**: Account A, Account B
- **Plan 2**: Account C, Account D
- **Plan 3**: Account E, Account F

For **Account A**, add this in the *Related Accounts* table:
- Plan B → Account D

**Result:** When you select **Account A** (Plan 1) in the
analytic_distribution field, only **Account D** will be available for
Plan 2 and all accounts will be available for Plan 3.
