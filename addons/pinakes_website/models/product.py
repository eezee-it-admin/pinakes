# Copyright 2023 Eezee-IT (<http://www.eezee-it.com>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
from odoo import api, fields, models
from random import randint

from odoo import models, fields, api


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    similar_products = fields.Many2many('product.template', compute='_compute_similar_products',
                                        string='Similar Products')
    common_categories_ids = fields.Many2many('product.public.category',
                                             compute='_compute_similar_products',
                                             string='Similar Categories')

    @api.depends('public_categ_ids')
    def _compute_similar_products(self):
        for product in self:
            product.similar_products = self.env['product.template'].browse([])
            product.common_categories_ids = self.env['product.public.category'].browse([])

            # Find products with shared public categories
            similar_products = self.env['product.template'].search(
                [('public_categ_ids', 'in', product.public_categ_ids.ids), ('id', '!=', product.id)]
            )

            # Filter based on the count of shared public categories
            similar_products_dict = {}
            for similar_product in similar_products:
                shared_categories_count = len(
                    set(similar_product.public_categ_ids.ids) & set(product.public_categ_ids.ids))
                if shared_categories_count > 0:  # You can set a threshold here
                    similar_products_dict[similar_product] = shared_categories_count

            # Sort products based on the number of shared public categories
            sorted_similar_products = sorted(similar_products_dict.items(), key=lambda x: x[1], reverse=True)

            # Update the similar products field and limit the number of similar products to a certain number (e.g., 6)
            product.similar_products = [(6, 0, [prod.id for prod, _ in sorted_similar_products[:6]])]

            # Compute common categories for each similar product
            for similar_product, _ in sorted_similar_products:
                common_categories = product.public_categ_ids & similar_product.public_categ_ids
                similar_product.common_categories_ids = [(6, 0, common_categories.ids)]
