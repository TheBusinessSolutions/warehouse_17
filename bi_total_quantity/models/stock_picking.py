# -*- coding: utf-8 -*-
from odoo import models, fields, api

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    demand_quantity = fields.Float(
        string='Total Demand Quantity',
        compute='_compute_total_demand_quantity',
        store=True,
        digits='Product Unit of Measure'
    )
    done_quantity = fields.Float(
        string='Total Done Quantity',
        compute='_compute_total_done_quantity',
        store=True,
        digits='Product Unit of Measure'
    )

    @api.depends('move_ids_without_package.product_uom_qty', 'move_ids_without_package.quantity')
    def _compute_total_demand_quantity(self):
        for picking in self:
            picking.demand_quantity = sum(picking.move_ids_without_package.mapped('product_uom_qty'))

    @api.depends('move_ids_without_package.product_uom_qty', 'move_ids_without_package.quantity')
    def _compute_total_done_quantity(self):
        for picking in self:
            picking.done_quantity = sum(picking.move_ids_without_package.mapped('quantity'))