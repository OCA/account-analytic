This feature proposes a strategy to track and report work in progress and variances.

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
