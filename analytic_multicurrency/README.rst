.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :alt: License: AGPL-3

Multi-Currency in Analytic Accounting
=====================================


This module improves OpenERP multi-currency handling in analytic
accounting, overall for multi-company.

This module is based on the work made in all c2c_multicost* available on
the v5.0 stable version and allows you to share analytic account between
company (even if currency differs in each one).

Features:

* Adapt the owner of analytic line (= to company that own the general
  account associated with an analytic line)

* Add multi-currency on analytic lines (similar to financial accounting)

* Correct all &quot;costs&quot; indicators into analytic account to base them on
  the right currency (owner's company)

* By default, nothing changes for single company implementation.

As a result, we can now really share the same analytic account between
companies that do not have the same currency. This setup becomes True,
Enjoy !

* Company A: EUR - Company B: CHF

* Analytic Account A: USD, owned by Company A

  - Analytic Account B: CHF, owned by Company A

  - Analytic Account C: EUR, owned by Company B


The difference with the regular 'Amount Currency':

* Regular 'Amount Currency' displays the amount currency of the related
  move line (only when linked with a move line, of course)
* Analytic Amount Currency displays the amount of the analytic move line
  converted to the right currency


Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/OCA/account-analytic/issues>`_.
In case of trouble, please check there if your issue has already been reported.
If you spotted it first, help us smashing it by providing a detailed and welcomed feedback
`here <https://github.com/OCA/account-analytic/issues/new?body=module:%20analytic_multicurrency%0Aversion:%201.0%0A%0A**Steps%20to%20reproduce**%0A-%20...%0A%0A**Current%20behavior**%0A%0A**Expected%20behavior**>`_.


Contributors
------------
* Guewen Baconnier <guewen.baconnier@camptocamp.com>
* Yannick Vaucher <yannick.vaucher@camptocamp.com>
* Vincent Renaville <charbel.jacquin@camptocamp.com>
* Charbel Jacquin <charbel.jacquin@camptocamp.com>

Maintainer
----------

.. image:: https://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: https://odoo-community.org

This module is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization whose
mission is to support the collaborative development of Odoo features and
promote its widespread use.

To contribute to this module, please visit http://odoo-community.org.
