# Copyright 2021      Eezee-IT (<http://www.eezee-it.com>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
from odoo import models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    def action_view_authors(self):
        self.ensure_one()
        action = self.env.ref(
            "politeia_extended.action_politeia_product_author"
        ).read([])[0]
        action['domain'] = [('product_tmpl_id', 'in', self.ids)]
        action['context'] = {
            'default_product_tmpl_id': self.id,
        }
        return action
