from odoo import models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    def write(self, vals):
        if not vals:
            return True
        # The Odoo core hash check blocks writes where integrity fields appear in vals,
        # even if unchanged. Updating analytic_distribution causes
        # _sync_dynamic_line to include account_id in the tax line write,
        # triggering a false positive. Strip unchanged integrity fields from
        # vals so the check only fires on real modifications.
        hashed = self.filtered(lambda line: line.move_id.inalterable_hash)
        if self.env.context.get("update_analytic") and hashed:
            integrity_fields = set(self._get_integrity_hash_fields()).union(
                {"inalterable_hash", "secure_sequence_number"}
            )
            unchanged = {
                fname
                for fname in integrity_fields & set(vals)
                if not any(
                    self.env["account.move"]._field_will_change(line, vals, fname)
                    for line in hashed
                )
            }
            if unchanged:
                vals = {k: v for k, v in vals.items() if k not in unchanged}
        return super().write(vals)
