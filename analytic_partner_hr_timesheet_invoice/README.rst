.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

==================================================
Invoice to the partner specified in analytic lines
==================================================

This module modifies analytic entries invoicing action for invoicing to
the "Other partner" specified on them. If no other partner is specified, then
the analytic account partner is used.

Installation
============

This module is auto-installed by Odoo when *analytic_partner* and
*analytic_partner_hr_timesheet* are installed.

Usage
=====

#. Go to *Sales > Invoicing > Sales to invoice* and select some of the lines
#. Click on *Action > Invoice Order*
#. Created invoice(s) will be split by the other partner field (if any), or the
   partner.

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/87/10.0


Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/OCA/account-analytic/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smash it by providing detailed and welcomed feedback.

Credits
=======

Images
------

* Thanks to https://openclipart.org/detail/201137/primary%20template%20invoice
* Thanks to https://openclipart.org/detail/15193/Arrow%20set%20%28Comic%29
* Odoo Community Association: `Icon <https://github.com/OCA/maintainer-tools/blob/master/template/module/static/description/icon.svg>`_.

Contributors
------------

* Pedro M. Baeza <pedro.baeza@tecnativa.com>
* Rafael Blasco <rafael.blasco@tecnativa.com>
* Luis M. Ontalba <luis.martinez@tecnativa.com>

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
