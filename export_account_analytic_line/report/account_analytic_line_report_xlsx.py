# Copyright 2026 Heliconia Solutions Pvt. Ltd.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, models

from odoo.addons.report_xlsx_helper.report.report_xlsx_format import (
    FORMATS,
    XLS_HEADERS,
)


class AccountAnalyticLineXlsx(models.AbstractModel):
    _name = "report.odvi_account_analytic_line_report_xls.aal_xlsx"
    _inherit = "report.report_xlsx.abstract"
    _description = "XLSX report for account analytic lines."

    def _get_ws_params(self, workbook, data, amls):
        # XLSX Template
        col_specs = {
            "move_line_id": {
                "header": {
                    "value": _("Journal Entry"),
                    "format": FORMATS["format_theader_yellow_center"],
                },
                "lines": {
                    "value": self._render(
                        "line.move_line_id.move_id and line.move_line_id.move_id.name"
                    )
                },
                "width": 18,
            },
            "general_account_id": {
                "header": {
                    "value": _("Financial Account"),
                    "format": FORMATS["format_theader_yellow_center"],
                },
                "lines": {
                    "value": self._render(
                        "line.general_account_id and line.general_account_id.name"
                    )
                },
                "width": 28,
            },
            "name": {
                "header": {
                    "value": _("Description"),
                    "format": FORMATS["format_theader_yellow_center"],
                },
                "lines": {"value": self._render("line.name")},
                "width": 42,
            },
            "date": {
                "header": {
                    "value": _("Date"),
                    "format": FORMATS["format_theader_yellow_center"],
                },
                "lines": {
                    "value": self._render("line.date"),
                    "format": FORMATS["format_tcell_date_left"],
                },
                "width": 13,
            },
            "ref": {
                "header": {
                    "value": _("Ref."),
                    "format": FORMATS["format_theader_yellow_center"],
                },
                "lines": {"value": self._render("line.ref or ''")},
                "width": 42,
            },
            "partner": {
                "header": {
                    "value": _("Partner"),
                    "format": FORMATS["format_theader_yellow_center"],
                },
                "lines": {
                    "value": self._render("line.partner_id and line.partner_id.name")
                },
                "width": 24,
            },
            "product_id": {
                "header": {
                    "value": _("Product"),
                    "format": FORMATS["format_theader_yellow_center"],
                },
                "lines": {
                    "value": self._render("line.product_id and line.product_id.name")
                },
                "width": 24,
            },
            "unit_amount": {
                "header": {
                    "value": _("Quantity"),
                    "format": FORMATS["format_theader_yellow_right"],
                },
                "lines": {
                    "value": self._render("line.unit_amount"),
                    "format": FORMATS["format_tcell_amount_right"],
                },
                "width": 13,
            },
            "product_uom_id": {
                "header": {
                    "value": _("Unit of Measure"),
                    "format": FORMATS["format_theader_yellow_center"],
                },
                "lines": {
                    "value": self._render(
                        "line.product_uom_id and line.product_uom_id.name"
                    )
                },
                "width": 16,
            },
            "tag_ids": {
                "header": {
                    "value": _("Tags"),
                    "format": FORMATS["format_theader_yellow_center"],
                },
                "lines": {
                    "value": self._render("','.join(line.tag_ids.mapped('name'))")
                },
                "width": 24,
            },
            "amount": {
                "header": {
                    "value": _("Amount"),
                    "format": FORMATS["format_theader_yellow_right"],
                },
                "lines": {
                    "value": self._render("line.amount"),
                    "format": FORMATS["format_tcell_amount_right"],
                },
                "totals": {
                    "type": "formula",
                    "value": self._render("amount_formula"),
                    "format": FORMATS["format_theader_yellow_amount_right"],
                },
                "width": 18,
            },
        }
        col_specs.update(self.env["account.analytic.line"]._report_xlsx_template())
        wanted_list = self.env["account.analytic.line"]._report_xlsx_fields()
        title = _("Analytic P&L Report")
        return [
            {
                "ws_name": title,
                "generate_ws_method": "_aals_export",
                "title": title,
                "wanted_list": wanted_list,
                "col_specs": col_specs,
            }
        ]

    def _aals_export(self, workbook, ws, ws_params, data, aals):
        ws.set_landscape()
        ws.fit_to_pages(1, 0)
        ws.set_header(XLS_HEADERS["xls_headers"]["standard"])
        ws.set_footer(XLS_HEADERS["xls_footers"]["standard"])

        self._set_column_width(ws, ws_params)

        row_pos = 0
        row_pos = self._write_ws_title(ws, row_pos, ws_params)

        row_pos = self._write_line(
            ws,
            row_pos,
            ws_params,
            col_specs_section="header",
            default_format=FORMATS["format_theader_yellow_left"],
        )

        ws.freeze_panes(row_pos, 0)

        wanted_list = ws_params["wanted_list"]

        analytic_columns_data_dict = self.env[
            "account.analytic.line"
        ]._get_analytic_columns_data()
        for line in aals:
            render_space = {"line": line}
            for col_data in analytic_columns_data_dict:
                fname = col_data.get("column_name")
                if fname:
                    render_space.update(
                        {fname: (v1 := getattr(line, fname)) and v1.name or ""}
                    )
            row_pos = self._write_line(
                ws,
                row_pos,
                ws_params,
                col_specs_section="lines",
                render_space=render_space,
                default_format=FORMATS["format_tcell_left"],
            )

        aal_cnt = len(aals)
        amount_pos = "amount" in wanted_list and wanted_list.index("amount")
        amount_start = self._rowcol_to_cell(row_pos - aal_cnt, amount_pos)
        amount_stop = self._rowcol_to_cell(row_pos - 1, amount_pos)
        amount_formula = f"SUM({amount_start}:{amount_stop})"
        self._write_line(
            ws,
            row_pos,
            ws_params,
            col_specs_section="totals",
            render_space={
                "amount_formula": amount_formula,
            },
            default_format=FORMATS["format_theader_yellow_left"],
        )
