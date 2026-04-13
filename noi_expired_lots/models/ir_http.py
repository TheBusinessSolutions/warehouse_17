# -*- coding: utf-8 -*-
###############################################################################
#    NexOrionis Techspere
###############################################################################
from odoo import models


class IrHttp(models.AbstractModel):
    """This class is used to add additional functionality to the 'ir.http'
    model. It inherits from the models.AbstractModel' class, allowing it to
    extend the behavior of the 'ir.http' model."""
    _inherit = 'ir.http'

    def session_info(self):
        """Get additional session information."""
        res = super().session_info()
        res['hide_filters_groupby'] = self.env[
            'ir.config_parameter'
        ].sudo().get_param('hide_filters_groupby.hide_filters_groupby')
        res['ir_model_ids'] = self.env[
            'ir.config_parameter'].sudo().get_param(
            'hide_filters_groupby.ir_model_ids')
        res['is_hide_filters_groupby_enabled'] = self.env[
            'ir.config_parameter'].sudo().get_param(
            'hide_filters_groupby.is_hide_filters_groupby_enabled')
        return res
