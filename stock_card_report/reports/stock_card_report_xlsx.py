# -*- coding: utf-8 -*-
# Clean Odoo 17 XLSX version for stock_card_report

from odoo import models


class ReportStockCardReportXlsx(models.AbstractModel):
    _name = "report.stock_card_report.report_stock_card_report_xlsx"
    _description = "Stock Card Report XLSX"
    _inherit = "report.report_xlsx.abstract"

    def generate_xlsx_report(self, workbook, data, reports):
        # ---------- Formats ----------
        fmt_title = workbook.add_format({
            "bold": True,
            "font_size": 14,
            "align": "center",
            "valign": "vcenter",
        })

        fmt_head = workbook.add_format({
            "bold": True,
            "border": 1,
            "align": "center",
            "valign": "vcenter",
        })

        fmt_text = workbook.add_format({
            "border": 1,
            "align": "left",
        })

        fmt_center = workbook.add_format({
            "border": 1,
            "align": "center",
        })

        fmt_num = workbook.add_format({
            "border": 1,
            "align": "right",
            "num_format": "#,##0.000",
        })

        fmt_bold_num = workbook.add_format({
            "bold": True,
            "border": 1,
            "align": "right",
            "num_format": "#,##0.000",
        })

        # ---------- Reports ----------
        for report in reports:
            for product in report.product_ids:
                sheet_name = f"{product.id}-{product.display_name}"[:31]
                ws = workbook.add_worksheet(sheet_name)

                # Columns
                ws.set_column("A:A", 18)   # Date
                ws.set_column("B:B", 28)   # Reference
                ws.set_column("C:C", 25)   # Lot
                ws.set_column("D:D", 25)   # Partner
                ws.set_column("E:G", 14)   # Qty cols

                row = 0

                # ---------- Title ----------
                ws.merge_range(row, 0, row, 6,
                               f"Stock Card - {product.display_name}",
                               fmt_title)
                row += 2

                # ---------- Filters ----------
                ws.write(row, 0, "Date From", fmt_head)
                ws.write(row, 1, "Date To", fmt_head)
                ws.write(row, 2, "Location", fmt_head)
                row += 1

                ws.write(row, 0, str(report.date_from or ""), fmt_center)
                ws.write(row, 1, str(report.date_to or ""), fmt_center)
                ws.write(
                    row,
                    2,
                    report.location_id.display_name if report.location_id else "",
                    fmt_text,
                )
                row += 2

                # ---------- Table Header ----------
                headers = [
                    "Date",
                    "Reference",
                    "Lot / Serial",
                    "Partner",
                    "In",
                    "Out",
                    "Balance",
                ]

                for col, header in enumerate(headers):
                    ws.write(row, col, header, fmt_head)

                row += 1

                # ---------- Opening Balance ----------
                initial_lines = report.results.filtered(
                    lambda l: l.product_id == product and l.is_initial
                )

                balance = report._get_initial(initial_lines)

                ws.write(row, 0, "", fmt_text)
                ws.write(row, 1, "Initial", fmt_text)
                ws.write(row, 2, "", fmt_text)
                ws.write(row, 3, "", fmt_text)
                ws.write(row, 4, "", fmt_text)
                ws.write(row, 5, "", fmt_text)
                ws.write(row, 6, balance, fmt_bold_num)

                row += 1

                # ---------- Transactions ----------
                lines = report.results.filtered(
                    lambda l: l.product_id == product and not l.is_initial
                )

                for line in lines:
                    balance += (line.product_in or 0.0) - (line.product_out or 0.0)

                    ws.write(
                        row,
                        0,
                        line.date.strftime("%Y-%m-%d %H:%M")
                        if line.date else "",
                        fmt_center,
                    )

                    ws.write(
                        row,
                        1,
                        line.picking_id.name
                        if line.picking_id else (line.reference or ""),
                        fmt_text,
                    )

                    ws.write(
                        row,
                        2,
                        getattr(line, "lot_names", "") or "",
                        fmt_text,
                    )

                    ws.write(
                        row,
                        3,
                        line.partner_id.name
                        if getattr(line, "partner_id", False) else "",
                        fmt_text,
                    )

                    ws.write(row, 4, line.product_in or 0.0, fmt_num)
                    ws.write(row, 5, line.product_out or 0.0, fmt_num)
                    ws.write(row, 6, balance, fmt_num)

                    row += 1