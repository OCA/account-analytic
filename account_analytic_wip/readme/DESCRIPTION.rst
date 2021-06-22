This feature proposes a strategy to track and report work in progress and variances.
The work in progress can be split in subitems, such as Labour and Overhead.

The base components are implemented here, a minimum viable process is working,
but the process is best leveraged by other apps, such as Projects or Manufacturing.

Resource consumption is to be recorded as Analytic Items
when operations are logged in the system of resources.

These Analytic Items are then used to calculate WIP and variances
versus the original expected amounts.
An "Analytic Tracking Items" object is used to hold the expected amount,
and calculate the WIP and variances to record.

A regular scheduled job uses that information
to generate the corresponding accounting moves.

Products can be seen as cost drivers, driving consumption of other items.
For example a machine work time can drive consumptions of Labor and Overhead.

This feature models cost driver usage as Analytic Items.
When an Analytic Item is created, it may then generate additional Analytic Items for the corresponding indirect costs.
For example, each timesheet hour logged could generate a quantity and amount of overhead assigned to that activity.
