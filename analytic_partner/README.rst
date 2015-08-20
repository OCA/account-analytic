Classify analytic items by partner
==================================

This module adds a partner on each analytic item for allowing to have another
dimension for analysing data.

It also handles the proper propagation of this field to the created analytic
entries when validating invoices.

Configuration
=============

You have to be granted as at least "Accountant" in your user profile and
have checked the "Analytic Accounting" access right.

Usage
=====

Go to Accounting > Analytic Journal Items, and there, you can set the partner
for the analytic items, and search or group by it.

You can also go to a partner, and click on the smart-button "Cost/Revenue",
placed on the upper-right part, and you will navigate to the analytic items
associated to this partner.


.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/87/8.0

Known issues / Roadmap
======================

* This module hasn't been tested with *account_analytic_plans* module
  installed, so maybe it's incompatible with it.

Credits
=======

Contributors
------------

* Pedro M. Baeza <pedro.baeza@serviciosbaeza.com>

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
