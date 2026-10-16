# Copyright 2021 Tecnativa - David Vidal
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import models


class PosSession(models.Model):
    _inherit = "pos.session"

    def _validate_session_accounting(self):
        return super(
            PosSession, self.with_context(pos_config_id=self.config_id.id)
        )._validate_session_accounting()
