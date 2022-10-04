.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

==============
Stock Analytic
==============

Adds an analytic account in stock move to be able to get analytic information
when generating the journal items.

Installation
============

To install this module, you need to:

1.  Clone the branch 8.0 of the repository https://github.com/OCA/account-analytic
2.  Add the path to this repository in your configuration (addons-path)
3.  Update the module list
4.  Go to menu *Setting -> Modules -> Local Modules*
5.  Search For *Stock Analytic*
6.  Install the module

Usage
=====

Assigned Stock Move With Analytic Account
-----------------------------------------

You need to:

#. Create manually or open draft picking
#. Add or edit stock move. Fill **analytic account** field

Assigned Journal Items created from Stock Move with Analytic Account
--------------------------------------------------------------------

If stock move automatically create journal entry, the journal entry will contain
journal items with following rule:

#. Journal item with account equal to product's valuation account will not be assigned
   any analytic account
#. Journal item with account not equal to product's valuation account will be assigned
   analytic account according to stock move's analytic account


.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/87/8.0

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

* Hanane ELKHAL <hanane@julius.fr>
* Yvan Patry <yvan@julius.fr>
* Pierre <pierre@julius.fr>
* Mathieu VATEL <mathieu@julius.fr>
* Fabio Vílchez <fabio.vilchez@clearcorp.co.cr>
* Andhitia Rama <andhitia.r@gmail.com>
* Michael Viriyananda <viriyananda.michael@gmai.com>

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
