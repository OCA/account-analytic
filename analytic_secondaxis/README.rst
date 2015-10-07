.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :alt: License: AGPL-3

Account Analytic Second Axis
============================

Add a second analytical axis on analytic lines allowing you to make
reporting on.

Unless the account_analytic_plans from Odoo SA, this module allow
you to make cross-reporting between those two axes, like all analytic
lines that concern for example:
The activity "Communication" and the project "Product 1 Integration".

This second axis is called "activities" and you will be able to define
for each analytical account, what are the allowed activities for it.

There's also a kind of heritage between analytical account. Adding
activities on parent account will allow child to benefit from. So you
can define a set of activities for each parent analytic account like:

Administrative
    - Intern
    - Project 1
Customers project
    - Project X
    - Project Y

What will be true for Administrative, will be true for Intern too.

Configuration
=============

Configure your ``Account Analytic Activities`` via this menu ``Accounting
> Configuration > Analytic Accounting > Account Analytic Activities``.
Via this menu you can define as many activities as you need.


Usage
=====

Menu entries are located in ``Accounting > Charts > Chart of Analytic Activities.``
Fill the two dates and click on the ``Open Charts`` Button

Credits
=======

Contributors
------------

* Joel Grand-guillaume
* Adil Houmadi <adil.houmadi@gmail.com>

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