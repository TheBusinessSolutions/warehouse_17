from odoo import models, fields, api

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    x_salesperson_name = fields.Char(
        string='Salesperson',
        compute='_compute_salesperson_name',
        store=False, # No need to store it in DB as it's computed on the fly for reports
    )

    @api.depends('origin')
    def _compute_salesperson_name(self):
        for picking in self:
            picking.x_salesperson_name = False
            if picking.origin:
                # The origin can contain multiple documents separated by commas, e.g., "SO001, SO002"
                # We usually take the first one or check if they belong to the same partner
                origins = picking.origin.split(',')
                sale_order = self.env['sale.order'].search([
                    ('name', 'in', [orig.strip() for orig in origins]),
                    ('state', '!=', 'cancel')
                ], limit=1)
                
                if sale_order and sale_order.user_id:
                    picking.x_salesperson_name = sale_order.user_id.name