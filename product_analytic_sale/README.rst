=====================
Product Analytic Sale
=====================

.. 
   !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
   !! This file is generated by oca-gen-addon-readme !!
   !! changes will be overwritten.                   !!
   !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
   !! source digest: sha256:6ec785e0658018720100573cb5ef2086c53ab48a6e7fc4714be1b6e8c405253a
   !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

.. |badge1| image:: https://img.shields.io/badge/maturity-Beta-yellow.png
    :target: https://odoo-community.org/page/development-status
    :alt: Beta
.. |badge2| image:: https://img.shields.io/badge/licence-AGPL--3-blue.png
    :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
    :alt: License: AGPL-3
.. |badge3| image:: https://img.shields.io/badge/github-OCA%2Faccount--analytic-lightgray.png?logo=github
    :target: https://github.com/OCA/account-analytic/tree/14.0/product_analytic_sale
    :alt: OCA/account-analytic
.. |badge4| image:: https://img.shields.io/badge/weblate-Translate%20me-F47D42.png
    :target: https://translation.odoo-community.org/projects/account-analytic-14-0/account-analytic-14-0-product_analytic_sale
    :alt: Translate me on Weblate
.. |badge5| image:: https://img.shields.io/badge/runboat-Try%20me-875A7B.png
    :target: https://runboat.odoo-community.org/builds?repo=OCA/account-analytic&target_branch=14.0
    :alt: Try me on Runboat

|badge1| |badge2| |badge3| |badge4| |badge5|

This module is a glue module between the modules **product_analytic** and **sale**.

The module **product_analytic** inherits the *create()* method of account.move.line to add the Analytic Account depending on the Product. But it is not enough in some specific scenarios: for exemple, if you have *Analytic Policy* set to *Required* on Revenue accounts and you have a sale tax configured with a revenue account and with the option *Include in Analytic Cost* enabled, then Odoo will not allow to create the invoice from a sale order. This module solves this issue by inheriting the method *_prepare_invoice_line()* of the sale order line.

**Table of contents**

.. contents::
   :local:

Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/OCA/account-analytic/issues>`_.
In case of trouble, please check there if your issue has already been reported.
If you spotted it first, help us to smash it by providing a detailed and welcomed
`feedback <https://github.com/OCA/account-analytic/issues/new?body=module:%20product_analytic_sale%0Aversion:%2014.0%0A%0A**Steps%20to%20reproduce**%0A-%20...%0A%0A**Current%20behavior**%0A%0A**Expected%20behavior**>`_.

Do not contact contributors directly about support or help with technical issues.

Credits
=======

Authors
~~~~~~~

* Akretion

Contributors
~~~~~~~~~~~~

* Alexis de Lattre <alexis.delattre@akretion.com>

Maintainers
~~~~~~~~~~~

This module is maintained by the OCA.

.. image:: https://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: https://odoo-community.org

OCA, or the Odoo Community Association, is a nonprofit organization whose
mission is to support the collaborative development of Odoo features and
promote its widespread use.

.. |maintainer-alexis-via| image:: https://github.com/alexis-via.png?size=40px
    :target: https://github.com/alexis-via
    :alt: alexis-via

Current `maintainer <https://odoo-community.org/page/maintainer-role>`__:

|maintainer-alexis-via| 

This module is part of the `OCA/account-analytic <https://github.com/OCA/account-analytic/tree/14.0/product_analytic_sale>`_ project on GitHub.

You are welcome to contribute. To learn how please visit https://odoo-community.org/page/Contribute.
