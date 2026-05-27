# -*- coding: utf-8 -*-
from odoo import models, fields, api

class AccountMove(models.Model):
    _inherit = 'account.move'

    # We rename these to reflect that they are based on Invoice Lines, 
    # not Pickings (since Sale module is missing)
    picking_demand_quantity = fields.Float(
        string='Total Billed Quantity',
        compute='_compute_invoice_quantities',
        digits='Product Unit of Measure',
        store=True
    )
    picking_done_quantity = fields.Float(
        string='Total Billed Quantity (Done)',
        compute='_compute_invoice_quantities',
        digits='Product Unit of Measure',
        store=True
    )

    # Depend ONLY on invoice_line_ids.quantity, which ALWAYS exists
    @api.depends('invoice_line_ids.quantity')
    def _compute_invoice_quantities(self):
        for invoice in self:
            total_qty = 0.0
            
            # Sum quantities from all product lines
            for line in invoice.invoice_line_ids:
                if line.product_id: # Only count product lines, not notes/sections
                    total_qty += line.quantity
            
            # For now, we set both to the same value since we don't have Picking data
            invoice.picking_demand_quantity = total_qty
            invoice.picking_done_quantity = total_qty