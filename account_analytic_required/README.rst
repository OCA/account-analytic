.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License

=========================
Account Analytic Required
=========================

This module adds an option *analytic policy* on account types.
You have the choice between 4 policies : *always*, *never*, *posted moves* and
*optional*.

Configuration
=============

For example, if you want to have an analytic account on all your expenses,
set the policy to *always* for the account type *expense* ; then, if you
try to save an account move line with an account of type *expense*
without analytic account, you will get an error message.

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

Contributors
------------
* Alexis de Lattre <alexis.delattre@akretion.com>
* Stéphane Bidoul
* Stefan Rijnhart
* Laetitia Gangloff
* Luc De Meyer, Noviat <info@noviat.com>
* Yannick Vaucher <yannick.vaucher@camptocamp.com>
* Akim Juillerat <akim.juillerat@camptocamp.com>

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
