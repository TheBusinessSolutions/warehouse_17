from odoo import api, models ,fields, _

class ExpiredLots(models.TransientModel):
    _name = 'expired.lots'

    name=fields.Char('Name')

