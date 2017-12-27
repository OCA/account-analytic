.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

======================
Analytic Tag Dimension
======================

This module allows to group Analytic Tags on Dimensions.

Dimensions are created as custom field, then you can group by Dimensions on:

* Account/Adviser/Journal Items
* Account/Reports/Business Intelligence/Analytic Entries

When you set Tags on Analytic Entries, each custom field for dimensions is updated with its Tag.

One Tag is only allowed on one Dimension, and you can not set more than one Tag from same Dimensions on Analytic Entry.


Configuration
=============

To configure this module, you need to:

* go to /Accounting/Configuration/Analytic Accounting/Analytic Accounts Dimensions to create new Analytic Dimensions.
* You can create new Analytic Tags on this form, or go to /Accounting/Configuration/Analytic Accounting/Analytic Accounts Tags and set Dimension for each Tag.


Known issues / Roadmap
======================

* Analytic Entries with Tags created before installing this module are not updated with theirs Dimensions.
* Set color on Analytic Dimensions, and get it on Analytic Tags.
* Change implementation to create stored computed fields, instead of rewrite create and write functions.
* On the function that create fields, get all the models that inherit from AbstractModel
* Set dimension on invoice report
* Improve fields_view_get to create filters on search view

Usage
=====

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/87/11.0

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

* Angel Moya <angel.moya@pesol.es>
* Artem Kostyuk <a.kostyuk@mobilunity.com>

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
