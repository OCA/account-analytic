.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

==================================================
Invoice to the partner specified in analytic lines
==================================================

This module modifies analytic entries invoicing action for invoicing to
the "Other partner" specified on them. If no other partner is specified, then
the analytic account partner is used.

Installation
============

This module is auto-installed by Odoo when *analytic_partner* and
*hr_timesheet_invoice* are installed.

Configuration
=============

You have to set the "Analytic Accounting" permission at user or db level for
seeing the analytic lines.

Usage
=====

Go to Accounting > Journal entries > Analytic Journal Items, and selecting some
of the lines, click on *More > Create Invoice*. Created invoice(s) will be
split by the other partner field (if any), or the analytic account partner.

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/87/8.0

Known issues / Roadmap
======================

* This module fully overwrites invoicing technical method
  (*invoice_cost_create*), so it's incompatible with other modules that also
  change something in the same method. If some hooks are provided on Odoo,
  this module can be changed for respecting inheritance chain.

Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/OCA/account-analytic/issues>`_.
In case of trouble, please check there if your issue has already been reported.
If you spotted it first, help us smashing it by providing a detailed and welcomed feedback
`here <https://github.com/OCA/account-analytic/issues/new?body=module:%20analytic_partner_hr_timesheet_invoice%0Aversion:%208.0%0A%0A**Steps%20to%20reproduce**%0A-%20...%0A%0A**Current%20behavior**%0A%0A**Expected%20behavior**>`_.

Credits
=======

Contributors
------------

* Pedro M. Baeza <pedro.baeza@serviciosbaeza.com>
* Rafael Blasco <rafabn@antiun.com>

Icon
----

* Thanks to https://openclipart.org/detail/201137/primary%20template%20invoice
* Thanks to https://openclipart.org/detail/15193/Arrow%20set%20%28Comic%29
* Original Odoo icons

Maintainer
----------

.. image:: http://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: http://odoo-community.org

This module is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization whose
mission is to support the collaborative development of Odoo features and
promote its widespread use.

To contribute to this module, please visit http://odoo-community.org.
