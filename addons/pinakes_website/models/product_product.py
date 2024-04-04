# Copyright 2023 Eezee-IT (<http://www.eezee-it.com>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import models
from odoo.http import request


class ProductTemplate(models.Model):
    _inherit = 'product.product'

    def get_all_variants(self, product_id):
        """This returns all possible combinations of variants for a product"""
        if product_id:
            product = request.env['product.product'].sudo().browse(int(product_id))
            if not product:
                return {'error': 'Product not found'}

            products = request.env['product.product'].sudo().search(
                [('product_tmpl_id', '=', product.product_tmpl_id.id)])

            variant_data = [{'id': variant.id, 'name': variant.display_name} for variant in products]

            return {'variants': variant_data}
