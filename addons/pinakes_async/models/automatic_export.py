# Copyright 2025 Eezee-IT (<http://www.eezee-it.com>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
from odoo import models, api


class AutomaticExport(models.AbstractModel):
    _inherit = 'automatic.export'

    @api.model
    def evaluate_domain(self, config):
        res = super().evaluate_domain(config)
        # Add custom sort logic here when the model is stock_move
        if res and config and config.model_name == 'stock.move':
            res = res.sorted(key=lambda r: r.sale_line_id.order_id.id)
        return res
