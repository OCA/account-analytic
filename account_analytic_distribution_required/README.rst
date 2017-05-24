.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

==============================
Account Analytic Plan Required
==============================

This module extends account_analytic_required and adds 2 policies to
control the use of analytic distributions. The policies behave as follow

* never: no analytic account nor analytic distribution allowed
* always: analytic account required
* always_plan: analytic_distribution required
* always_plan_or_account: analytic distribution or analytic account required
* optional: do what you like,

In any case analytic account and analytic distribution are mutually exclusive.


Configuration
=============

To configure this module, you need to:

#. Go to *Invoicing (or Accounting) > Configuration > Accounting > Account
   Types* and select the correct **Policy for analytic account** for every
   account type you want.

Usage
=====

To use this module, you need to:

#. Create an invoice and add a line with an account of the same type you
   are configured above.
#. Add an analytic distribution or an analytic account to that line.
#. When you validate the invoice you get a message if analytic account or
   distribution are incorrect.

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/87/10.0

Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/OCA/account-analytic/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smashing it by providing a detailed and welcomed feedback.

Credits
=======

Images
------

* Odoo Community Association: `Icon <https://github.com/OCA/maintainer-tools/blob/master/template/module/static/description/icon.svg>`_.

Contributors
------------

* Stéphane Bidoul <stephane.bidoul@acsone.eu>
* Vicent Cubells <vicent.cubells@tecnativa.com>

Maintainer
----------

.. image:: https://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: https://odoo-community.org

This module is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization whose
mission is to support the collaborative development of Odoo features and
promote its widespread use.

To contribute to this module, please visit https://odoo-community.org.
