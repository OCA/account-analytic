## Company Settings

1.  Go to *Accounting \> Configuration \> Settings*.
2.  In the *Analytics* section, configure:
    - **Indirect Costs Analytic Plans**: analytic plans whose accounts
      (and the accounts of their children plans) are considered indirect
      costs.
    - **Profit Centres Analytic Plans**: analytic plans whose accounts
      (and the accounts of their children plans) are considered profit
      centres.

## Distribution Models

1.  Go to *Accounting \> Configuration \> Analytic Accounting \>
    Indirect Cost Distribution Models*.
2.  Create a new distribution model:
    - **Name**: descriptive name for the model.
    - **Distribution Method**:
        - *Based on Timesheet*: distribute proportionally to timesheet
          hours registered in profit centres.
        - *Based on Profits*: distribute proportionally to profits
          (positive amounts) registered in profit centres.
    - **Indirect Cost Plans**: analytic plans containing indirect costs
      to be distributed. They must be under the configured indirect
      costs root plans.
    - **Profit Centre Plans**: analytic plans where costs will be
      distributed. They must be under the configured profit centres
      root plans.

Each analytic plan can only be assigned to one distribution model.
This prevents the same costs from being distributed multiple times.
