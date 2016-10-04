.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :alt: License

Account Analytic Required
=========================

This module adds an option *analytic policy* on account types.
You have the choice between 3 policies : *always*, *never* and *optional*.

Configuration
=============

For example, if you want to have an analytic account on all your expenses,
set the policy to *always* for the account type *expense* ; then, if you
try to save an account move line with an account of type *expense*
without analytic account, you will get an error message.

Usage
=====

The analytic account becomes a mandatory field on the User Interface when entering a transaction
on an account with analytic policy 'always'.

This functionality has been implemented for the following base transactions:

- Invoices
- Bank Statements
- Journal Items
- Journal Entries

For other transactions you will get an error message
at account move creation time when violating the analytic policy.

Credits
=======

Author
------
* Module developed by Alexis de Lattre <alexis.delattre@akretion.com>
  during the Akretion-Camptocamp code sprint of June 2011.

Contributors
------------
* Luc De Meyer, Noviat <info@noviat.com>

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