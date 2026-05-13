from odoo import models, fields

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    # We pull the user_id (Salesperson) from the linked Sale Order
    # 'sale_id' is provided by the sale_stock module
    salesperson_id = fields.Many2one(
        'res.users', 
        related='sale_id.user_id', 
        string="Salesperson", 
        readonly=True,
        store=True
    )