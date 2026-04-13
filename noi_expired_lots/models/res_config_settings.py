from odoo import api, models, fields
from odoo.tools._monkeypatches import literal_eval



class Company(models.Model):

    _inherit = 'res.company'

    expired_lot_block_a_duration = fields.Float('Block A Duration')
    expired_lot_block_a_duration_unit = fields.Selection([('days', 'Days'),
                                                          ('months', 'Months'),
                                                          ('years', 'Years')], 'Block A Duration Unit')
    expired_lot_block_a_color = fields.Char('Block A Color')
    expired_lot_block_b_duration = fields.Float('Block B Duration')
    expired_lot_block_b_duration_unit = fields.Selection([('days', 'Days'),
                                                          ('months', 'Months'),
                                                          ('years', 'Years')], 'Block B Duration Unit')
    expired_lot_block_b_color = fields.Char('Block B Color')
    expired_lot_block_c_duration = fields.Float('Block C Duration')
    expired_lot_block_c_duration_unit = fields.Selection([('days', 'Days'),
                                                          ('months', 'Months'),
                                                          ('years', 'Years')], 'Block C Duration Unit')
    expired_lot_block_c_color = fields.Char('Block C Color')
    expired_lot_color = fields.Char('Expired Lot Color')


class ResConfigSettings(models.TransientModel):

    _inherit = 'res.config.settings'

    expired_lot_block_a_duration = fields.Float('Block A Duration', related='company_id.expired_lot_block_a_duration', readonly=False)
    expired_lot_block_a_duration_unit = fields.Selection('Block A Duration Unit', related='company_id.expired_lot_block_a_duration_unit', readonly=False)
    expired_lot_block_a_color = fields.Char('Block A Color', related='company_id.expired_lot_block_a_color', readonly=False)
    expired_lot_block_b_duration = fields.Float('Block B Duration', related='company_id.expired_lot_block_b_duration', readonly=False)
    expired_lot_block_b_duration_unit = fields.Selection('Block B Duration Unit', related='company_id.expired_lot_block_b_duration_unit', readonly=False)
    expired_lot_block_b_color = fields.Char('Block B Color', related='company_id.expired_lot_block_b_color', readonly=False)
    expired_lot_block_c_duration = fields.Float('Block C Duration', related='company_id.expired_lot_block_c_duration', readonly=False)
    expired_lot_block_c_duration_unit = fields.Selection('Block C Duration Unit', related='company_id.expired_lot_block_c_duration_unit', readonly=False)
    expired_lot_block_c_color = fields.Char('Block C Color', related='company_id.expired_lot_block_c_color', readonly=False)
    expired_lot_color = fields.Char('Expired Lot Color', related='company_id.expired_lot_color', readonly=False)


    is_hide_filters_groupby_enabled = fields.Boolean(
        string='Hide Filters and Group By Enabled', default=True,
        config_parameter='hide_filters_groupby.is_hide_filters_groupby_enabled',
        help='If set to True, it enables hiding filters and group by globally.')
    hide_filters_groupby = fields.Selection(selection=[
        ('global', 'Globally'), ('custom', 'Custom'), ],
        string='Hide Filters and Group By', default='custom',
        config_parameter='hide_filters_groupby.hide_filters_groupby',
        help='Choose the option to hide filters and group by globally or'
             ' use custom settings.')
    ir_model_ids = fields.Many2many(
        'ir.model',
        'res_config_ir_model_rel',
        'res_config', 'model',
        string='Models',
        readonly=False,
        help='Models that are affected by the '
             'hide filters and group by settings.')

    def set_values(self):
        """this function helps to save values in the settings
         inherited choose_product_ids field"""
        res = super().set_values()
        self.env['ir.config_parameter'].sudo().set_param(
            'hide_filters_groupby.ir_model_ids',
            self.ir_model_ids.ids)
        return res

    @api.model
    def get_values(self):
        """this function retrieve the values from the ir_config_parameters"""
        res = super().get_values()
        model_ids = self.env['ir.config_parameter'].sudo().get_param(
            'hide_filters_groupby.ir_model_ids')
        res.update(
            ir_model_ids=[
                fields.Command.set(literal_eval(model_ids))
            ] if model_ids else False)
        return res