- Account mappings are applied direct-only, transitive chaining is not
  supported at the moment, to keep the logic cycle-free.
- Because the mapped account is re-added on every change, a destination account
  can't be removed from a line manually while source account is present.
