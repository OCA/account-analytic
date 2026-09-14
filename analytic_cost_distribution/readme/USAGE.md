## Running a Cost Distribution Operation

1.  Go to *Accounting \> Accounting \> Cost Distribution*.
2.  Create a new operation:
    - **Date From / Date To**: date range for indirect costs to
      distribute.
    - **Distribution Date**: the date that will be used for the
      created analytic lines.
3.  Click **Compute** to calculate the distribution. The system
    retrieves all analytic lines with negative amounts (costs) in the
    period that have not been distributed yet, groups them by
    distribution model, and computes the total amount per model. A
    warning is shown if some costs in the period have already been
    distributed by other operations (those lines are excluded).
4.  Review the computed distribution lines.
5.  Click **Distribute** to create the analytic lines:
    - For each profit centre a cost line is created proportional to the
      distribution method configured on the model.
    - The original indirect cost lines are marked as distributed and
      will be excluded from future distribution operations.
    - Indirect costs remain in their original accounts for traceability.
6.  The operation moves to *Done* state.

## Viewing distributed lines

Click the **Distributed Lines** smart button on the operation to see all
analytic lines created by the distribution.

## Resetting an operation

A *Done* operation can be reset back to *Draft*:

1.  Open the operation and click **Reset to Draft**.
2.  All distributed lines are deleted.
3.  The source indirect cost lines are unmarked as distributed and
    become available for new operations.

## Distribution logic

### Based on Timesheet

Each profit centre receives a portion of the indirect costs proportional
to its share of total timesheet hours in the period.

### Based on Profits

Each profit centre receives a portion of the indirect costs proportional
to its share of total profits (positive analytic amounts) in the period.

## Profit/Cost Category

Analytic lines are categorized via a stored, editable
`profit_cost_category` field. Possible values: *Customer Invoice*,
*Vendor Bill*, *Timesheet*, *Costs Distribution*, *Manual*, *Other*. The
field is available in the analytic lines list (optional column), form
view, and as a search/group-by criterion.
