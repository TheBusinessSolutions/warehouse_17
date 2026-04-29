# Copyright 2019 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import pytz
from odoo import api, fields, models


# stock_card_report.py - Key fixes shown

class StockCardView(models.TransientModel):
    _name = "stock.card.view"
    _description = "Stock Card View"
    _order = "date"
    
    date = fields.Datetime()
    product_id = fields.Many2one(comodel_name="product.product")  # Removed trailing space
    product_qty = fields.Float()
    product_uom_qty = fields.Float()
    product_uom = fields.Many2one(comodel_name="uom.uom")  # Removed trailing space
    reference = fields.Char()
    location_id = fields.Many2one(comodel_name="stock.location")  # Removed trailing space
    location_dest_id = fields.Many2one(comodel_name="stock.location")  # Removed trailing space
    is_initial = fields.Boolean()
    product_in = fields.Float()
    product_out = fields.Float()
    picking_id = fields.Many2one(comodel_name="stock.picking")  # Removed trailing space
    
    # NEW fields for report columns
    partner_id = fields.Many2one(comodel_name="res.partner", string="Partner")  # Removed trailing space
    description = fields.Char()
    location_from = fields.Char(string="From Location")  # Removed trailing space
    location_to = fields.Char(string="To Location")  # Removed trailing space
    source_document = fields.Char(string="Source Document")  # Removed trailing space

    def name_get(self):
        result = []
        for rec in self:
            name = rec.picking_id.name if rec.picking_id else (rec.reference or "")
            if rec.picking_id and rec.picking_id.origin:
                name = "{} ({})".format(name, rec.picking_id.origin)
            result.append((rec.id, name))
        return result


class StockCardReport(models.TransientModel):
    _name = "report.stock.card.report"
    _description = "Stock Card Report"
    
    # Filters fields
    date_from = fields.Date()
    date_to = fields.Date()
    product_ids = fields.Many2many(comodel_name="product.product")  # Removed trailing space
    location_id = fields.Many2one(comodel_name="stock.location")  # Removed trailing space, made optional

    # Data fields
    results = fields.Many2many(
        comodel_name="stock.card.view",  # Removed trailing space
        compute="_compute_results",  # Removed trailing space
        help="Use compute fields, so there is nothing stored in database",  # Removed trailing space
    )

    def _compute_results(self):
        self.ensure_one()
        date_from = self.date_from or "0001-01-01"  # Removed trailing space
        date_to = self.date_to or fields.Date.context_today(self)
        
        # Handle optional location - all company locations if empty
        if self.location_id:
            locations = self.env["stock.location"].search(  # Removed trailing space
                [("id", "child_of", [self.location_id.id])]  # Removed trailing space
            )
        else:
            warehouses = self.env["stock.warehouse"].search(  # Removed trailing space
                [("company_id", "=", self.env.company.id)]  # Removed trailing space
            )
            location_ids = []
            for wh in warehouses:
                all_locs = self.env["stock.location"].search(
                    [("id", "child_of", wh.lot_stock_id.ids)]
                )
                location_ids.extend(all_locs.ids)
            locations = self.env["stock.location"].browse(list(set(location_ids)))
        
        location_ids = tuple(locations.ids) if locations.ids else (0,)
        product_ids = tuple(self.product_ids.ids) if self.product_ids.ids else (0,)
        
        # FIXED SQL query - removed typos and trailing spaces
        self._cr.execute(
            """
            SELECT move.date, move.product_id, move.product_qty,
                move.product_uom_qty, move.product_uom, move.reference,
                move.location_id, move.location_dest_id,
                CASE WHEN move.location_dest_id IN %s
                    THEN move.product_qty ELSE 0 END as product_in,
                CASE WHEN move.location_id IN %s
                    THEN move.product_qty ELSE 0 END as product_out,
                CASE WHEN move.date < %s THEN TRUE ELSE FALSE END as is_initial,
                move.picking_id,
                move.partner_id,
                move.name as description,
                loc_src.name as location_from,
                loc_dest.name as location_to,
                COALESCE(picking.origin, picking.name, move.reference) as source_document
            FROM stock_move move
            LEFT JOIN stock_location loc_src ON move.location_id = loc_src.id
            LEFT JOIN stock_location loc_dest ON move.location_dest_id = loc_dest.id
            LEFT JOIN stock_picking picking ON move.picking_id = picking.id
            WHERE (move.location_id IN %s OR move.location_dest_id IN %s)
                AND move.state = 'done' 
                AND move.product_id IN %s
                AND CAST(move.date AS date) <= %s
            ORDER BY move.date, move.reference
            """,
            (
                location_ids,
                location_ids,
                date_from,
                location_ids,
                location_ids,
                product_ids,
                date_to,
            ),
        )
        stock_card_results = self._cr.dictfetchall()
        ReportLine = self.env["stock.card.view"]  # Removed trailing space
        user_tz = self.env.user.tz or "UTC"  # Removed trailing space
        user_timezone = pytz.timezone(user_tz)
        new_results = []
        for line in stock_card_results:
            if line["date"]:
                line["date"] = line["date"].astimezone(user_timezone).replace(tzinfo=None)
            new_results.append(ReportLine.new(line).id)
        self.results = new_results

    def _get_initial(self, product_line):
        product_input_qty = sum(product_line.mapped("product_in"))  # Removed trailing space
        product_output_qty = sum(product_line.mapped("product_out"))  # Removed trailing space
        return product_input_qty - product_output_qty

    def print_report(self, report_type="qweb"):  # Removed trailing space
        self.ensure_one()
        if report_type == "xlsx":  # Removed trailing space
            action = self.env.ref("stock_card_report.action_stock_card_report_xlsx")  # Removed trailing space
        else:
            action = self.env.ref("stock_card_report.action_stock_card_report_pdf")  # Removed trailing space
        return action.report_action(self, config=False)

    def _get_html(self):
        result = {}
        rcontext = {}
        report = self.browse(self._context.get("active_id"))  # Removed trailing space
        if report:
            rcontext["o"] = report  # Removed trailing space
            result["html"] = self.env["ir.qweb"]._render(  # Removed trailing space
                "stock_card_report.report_stock_card_report_html", rcontext  # Removed trailing space
            )
        return result

    @api.model
    def get_html(self, given_context=None):
        return self.with_context(**(given_context or {}))._get_html()