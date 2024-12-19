Using this module is straightforward. Follow these steps:

* **Navigate to the Report**:  
  Go to **Invoicing** -> **Reporting** -> **Analytic Trial Balance**.

* **Customize the Report with Filters**:  
  Adjust the report using the available options:

  * **Group by Analytic Account**:  
    Groups the results by analytic accounts instead of financial accounts.

  * **Show Hierarchy and Limit Hierarchy Level**:  
    Displays the amounts split by the hierarchy levels of financial accounts.

  * **Filter Accounts**:  
    When used independently (without grouping by analytic accounts or showing hierarchy), the results will be split by both financial accounts.  
    **Example**: Filtering by accounts *Test 1* and *Test 2*:

    ```text
            | Initial Balance | Test 1   | Test 2   | Ending Balance
    400000  |        0        | $3600    | $2400    |     $6000
    ```

  * **Show Months** (Excel export only):  
    Enabled when filtering accounts without grouping by analytic accounts or showing hierarchy. It generates a separate sheet in the Excel file for each filtered account, detailing the amounts by month within the selected date range.  
