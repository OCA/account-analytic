Technical module to add account department to timesheet analysis report.
This module is also needed to avoid having an issue related to ``account_department_id``.
When the module hr_timesheet is also installed, the issue is raised of non-existing field ``account_department_id`` on model ``timesheets.analysis.report``.
This happens, because ``hr_timesheet.hr_timesheet_report_search`` view defined for model ``timesheets.analysis.report`` is inherited from ``hr_timesheet.hr_timesheet_line_search`` view defined for model ``account.analytic.line``.
