# Copyright 2024 Your Company
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import pytz
from odoo import api, fields, models


class StockCardView(models.TransientModel):
    _name = "stock.card.view"
    _description = "Stock Card View"
    _order = "date"

    date = fields.Datetime()
    product_id = fields.Many2one(comodel_name="product.product")
    product_qty = fields.Float()
    product_uom_qty = fields.Float()
    product_uom = fields.Many2one(comodel_name="uom.uom")
    reference = fields.Char()
    location_id = fields.Many2one(comodel_name="stock.location")
    location_dest_id = fields.Many2one(comodel_name="stock.location")
    is_initial = fields.Boolean()
    product_in = fields.Float()
    product_out = fields.Float()
    picking_id = fields.Many2one(comodel_name="stock.picking")
    
    # Additional fields for detailed report
    partner_id = fields.Many2one(comodel_name="res.partner", string="Partner")
    description = fields.Char()
    location_from = fields.Char(string="From Location")
    location_to = fields.Char(string="To Location")
    source_document = fields.Char(string="Source Document")

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

    # Filter fields
    date_from = fields.Date()
    date_to = fields.Date()
    product_ids = fields.Many2many(comodel_name="product.product")
    
    # FIXED: Changed to Many2many for multi-location support
    location_ids = fields.Many2many(comodel_name="stock.location")

    # Computed data field
    results = fields.Many2many(
        comodel_name="stock.card.view",
        compute="_compute_results",
        help="Use compute fields, so there is nothing stored in database",
    )

    def _compute_results(self):
        self.ensure_one()
        date_from = self.date_from or "0001-01-01"
        date_to = self.date_to or fields.Date.context_today(self)
        
        # FIXED: Handle location filtering - 3 scenarios
        if self.location_ids:
            # Scenario 1 & 2: User selected one or multiple locations
            # Get the selected locations AND their child locations
            location_domain = [('id', 'child_of', self.location_ids.ids)]
            locations = self.env["stock.location"].search(location_domain)
        else:
            # Scenario 3: No location selected - get ALL company stock locations
            warehouses = self.env["stock.warehouse"].search(
                [('company_id', '=', self.env.company.id)]
            )
            location_ids = []
            for wh in warehouses:
                # Get all stock locations under this warehouse
                wh_locations = self.env["stock.location"].search(
                    [('id', 'child_of', wh.lot_stock_id.ids)]
                )
                location_ids.extend(wh_locations.ids)
            locations = self.env["stock.location"].browse(list(set(location_ids)))
        
        # Prepare location IDs tuple for SQL (handle empty case)
        location_ids_tuple = tuple(locations.ids) if locations.ids else (0,)
        product_ids_tuple = tuple(self.product_ids.ids) if self.product_ids.ids else (0,)
        
        # FIXED: Enhanced SQL query with proper JOINs for additional fields
        query = """
            SELECT 
                move.date, 
                move.product_id, 
                move.product_qty,
                move.product_uom_qty, 
                move.product_uom, 
                move.reference,
                move.location_id, 
                move.location_dest_id,
                -- Calculate product_in: qty when destination is in selected locations
                CASE 
                    WHEN move.location_dest_id IN %s THEN move.product_qty 
                    ELSE 0 
                END as product_in,
                -- Calculate product_out: qty when source is in selected locations  
                CASE 
                    WHEN move.location_id IN %s THEN move.product_qty 
                    ELSE 0 
                END as product_out,
                -- Mark initial balance records (before date_from)
                CASE 
                    WHEN move.date < %s THEN TRUE 
                    ELSE FALSE 
                END as is_initial,
                move.picking_id,
                -- Additional fields for detailed display
                move.partner_id,
                COALESCE(picking.name, move.name, move.reference) as description,
                loc_src.complete_name as location_from,
                loc_dest.complete_name as location_to,
                COALESCE(picking.origin, picking.name, move.reference) as source_document
            FROM stock_move move
            LEFT JOIN stock_location loc_src ON move.location_id = loc_src.id
            LEFT JOIN stock_location loc_dest ON move.location_dest_id = loc_dest.id
            LEFT JOIN stock_picking picking ON move.picking_id = picking.id
            WHERE 
                (move.location_id IN %s OR move.location_dest_id IN %s)
                AND move.state = 'done' 
                AND move.product_id IN %s
                AND CAST(move.date AS date) <= %s
            ORDER BY move.date, move.reference, move.id
        """
        
        self._cr.execute(
            query,
            (
                location_ids_tuple,  # for product_in CASE
                location_ids_tuple,  # for product_out CASE
                date_from,           # for is_initial CASE
                location_ids_tuple,  # for WHERE location_id
                location_ids_tuple,  # for WHERE location_dest_id
                product_ids_tuple,   # for WHERE product_id
                date_to,             # for WHERE date
            ),
        )
        
        stock_card_results = self._cr.dictfetchall()
        ReportLine = self.env["stock.card.view"]
        
        # Handle timezone conversion
        user_tz = self.env.user.tz or "UTC"
        user_timezone = pytz.timezone(user_tz)
        
        new_results = []
        for line in stock_card_results:
            if line.get("date"):
                # Convert to user timezone and remove tzinfo for consistent display
                line["date"] = line["date"].astimezone(user_timezone).replace(tzinfo=None)
            # Create transient record and collect ID
            new_results.append(ReportLine.new(line).id)
        
        self.results = new_results

    def _get_initial(self, product_line):
        """Calculate initial balance for a product"""
        product_input_qty = sum(product_line.mapped("product_in"))
        product_output_qty = sum(product_line.mapped("product_out"))
        return product_input_qty - product_output_qty

    def print_report(self, report_type="qweb"):
        self.ensure_one()
        if report_type == "xlsx":
            action = self.env.ref("stock_card_report.action_stock_card_report_xlsx")
        else:
            action = self.env.ref("stock_card_report.action_stock_card_report_pdf")
        return action.report_action(self, config=False)

    def _get_html(self):
        result = {}
        rcontext = {}
        report = self.browse(self._context.get("active_id"))
        if report:
            rcontext["o"] = report
            result["html"] = self.env["ir.qweb"]._render(
                "stock_card_report.report_stock_card_report_html", rcontext
            )
        return result

    @api.model
    def get_html(self, given_context=None):
        return self.with_context(**(given_context or {}))._get_html()