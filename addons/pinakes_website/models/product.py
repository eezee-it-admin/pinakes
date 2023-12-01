# Copyright 2023 Eezee-IT (<http://www.eezee-it.com>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
from odoo import api, fields, models
from random import randint


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    similar_products = fields.Many2many('product.template', compute='_compute_similar_products',
                                        string='Similar Products')
    common_tags_ids = fields.Many2many('product.tag', 'product_tag_product_template_rel',
                                       compute='_compute_similar_products', string='Similar Tags')

    @api.depends('product_tag_ids')
    def _compute_similar_products(self):
        for product in self:
            product.common_tags_ids = self.env['product.tag'].browse([])
            similar_tags = product.product_tag_ids
            similar_products = self.env['product.template'].search(
                [('product_tag_ids', 'in', similar_tags.ids), ('id', '!=', product.id)])
            product.similar_products = similar_products
            for similar_product in similar_products:
                similar_product_tags = similar_product.product_tag_ids
                similar_product.common_tags_ids = self.env['product.tag'].search(
                    ['&',
                     ('id', 'in', similar_tags.ids),
                     ('id', 'in', similar_product_tags.ids)]
                )
