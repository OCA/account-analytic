.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

=============================
Purchase Procurement analytic
=============================

This module takes account analytic value from procurements to the created
purchase order line.

Configuration
=============

To configure this module, you need to:

#. Go to your user settings.
#. Enable *Analytic Accounting for Purchases* in *Technical Settings*.

Usage
=====

#. Go to *Inventory > Reports > Procurement Exceptions* and create a new one.
#. Set *Analytic Account* in *Extra Information* tab.
#. *Run Procurement*
#. The generated purchase order line will have this analytic account.
   They won't be grouped if analytic account is different.

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/87/10.0

Known issues / Roadmap
======================

* If product supplier info min quantity is greater than procurement qty and we
  have sale orders with distinct analytic account which contains this product,
  each purchase order line takes seller min quantity.

Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/OCA/account-analytic/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smashing it by providing a detailed and welcomed feedback.

Credits
=======

Contributors
------------
* Carlos Dauden <carlos.dauden@tecnativa.com>
* Pedro M. Baeza <pedro.baeza@tecnativa.com>
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
