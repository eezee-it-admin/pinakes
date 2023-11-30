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
    category_tags_ids = fields.Many2many('product.tag', compute='_compute_category_tags', string='Category Tags')

    @api.depends('categ_id')
    def _compute_category_tags(self):
        for product in self:
            rels = self.env['product.category.tag.rel'].search([('category_id', '=', product.categ_id.id)])
            product.category_tags_ids = rels.mapped('tag_id')

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


class ProductPublicCategoryTagRel(models.Model):
    _name = 'product.public.category.tag.rel'
    _description = 'Product Public Category Tag Relation'

    category_id = fields.Many2one('product.public.category', string='Category', required=True)
    tag_id = fields.Many2one('product.public.category.tag', string='Tag', required=True)


class ProductPublicCategory(models.Model):
    _inherit = 'product.public.category'
    _description = 'Product Public Category'

    tag_ids = fields.Many2many('product.public.category.tag', string='Category tags')


class ProductPublicCategoryTag(models.Model):
    _name = 'product.public.category.tag'
    _description = 'Product Public Category Tag'

    def _get_default_color(self):
        return randint(1, 11)

    name = fields.Char(required=True, string='Name')
    color = fields.Integer('Color', default=_get_default_color)
