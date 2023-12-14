# Copyright 2023 Eezee-IT (<http://www.eezee-it.com>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    similar_products = fields.Many2many('product.template', compute='_compute_similar_products')
    common_tags_ids = fields.Many2many('product.tag', 'product_tag_product_template_rel',
                                       compute='_compute_similar_products', string='Similar Tags')

    @api.depends('product_tag_ids')
    def _compute_similar_products(self):
        for product in self:
            product.similar_products = self.env['product.template'].browse([])
            product.common_tags_ids = self.env['product.tag'].browse([])

            similar_products = self.env['product.template'].search(
                [('product_tag_ids', 'in', product.product_tag_ids.ids), ('id', '!=', product.id)]
            )

            similar_products_dict = {}
            for similar_product in similar_products:
                shared_tags_count = len(set(similar_product.product_tag_ids.ids) & set(product.product_tag_ids.ids))
                if shared_tags_count > 0:
                    similar_products_dict[similar_product] = shared_tags_count

            sorted_similar_products = sorted(similar_products_dict.items(), key=lambda x: x[1], reverse=True)

            product.similar_products = [(6, 0, [prod.id for prod, _ in sorted_similar_products[:6]])]

            for similar_product, _ in sorted_similar_products:
                common_tags = product.product_tag_ids & similar_product.product_tag_ids
                similar_product.common_tags_ids = [(6, 0, common_tags.ids)]

    @api.model
    def _search_get_detail(self, website, order, options):
        detail = super(ProductTemplate, self)._search_get_detail(website, order, options)

        tag_ids = options.get('product_tag_ids')
        if tag_ids:
            detail['base_domain'].append([('product_tag_ids', 'in', tag_ids)])

        # Search by the isbn on product variants
        detail['search_fields'].append('product_variant_ids.isbn')
        detail['mapping']['product_variant_ids.isbn'] = {'name': 'product_variant_ids.isbn', 'type': 'text',
                                                         'match': True}

        # Search on authors name
        detail['search_fields'].append('product_author_names')
        detail['mapping']['product_author_names'] = {'name': 'product_author_names', 'type': 'text', 'match': True}

        return detail
