.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :alt: License

Restrict Analytic Journal on Company
====================================

This module prevents users from creating journals for a company that refer
to an analytic journal of another company.

Both the chart of accounts and analytic accounts should be kept strictly
separate for different companies.

Installation
============

After installing this module no more journals can be created that refer to
the analytic journals of another company. However existing wrong
configurations are not (and cannot) be automatically corrected. To check
wether such wrong configurations exist use the following SQL:

```
# select
    aj.id, aj.name, aj.company_id,
    aaj.id, aaj.name, aaj.company_id, rc.name
from account_journal aj 
join account_analytic_journal aaj on aj.analytic_journal_id = aaj.id
join res_company rc on aj.company_id = rc.id
where aj.company_id != aaj.company_id;
```


More info
---------

For further information, please visit:

 * https://www.odoo.com/forum/help-1

Known issues / Roadmap
======================

Credits
=======

Contributors
------------

* Ronald Portier <ronald@therp.nl>

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
