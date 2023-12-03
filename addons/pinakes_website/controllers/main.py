# Copyright 2023      Eezee-IT (<http://www.eezee-it.com>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
from odoo import http
from odoo.http import request
from odoo.osv import expression
from odoo.addons.website_sale.controllers.main import WebsiteSale

import pprint


class WebsiteSaleExtendedSearch(WebsiteSale):

    def _get_search_domain(self, search, category, attrib_values, search_in_description=True):
        # Base domains from the super method
        domains = super(WebsiteSaleExtendedSearch, self)._get_search_domain(search, category, attrib_values,
                                                                            search_in_description)

        if search:
            matching_variants = request.env['product.product'].search([('isbn', 'ilike', search)])
            matching_templates_ids = matching_variants.mapped('product_tmpl_id').ids

            author_products = request.env['product.author'].search([('partner_id.name', 'ilike', search)]).mapped(
                'product_tmpl_id')
            author_domain = [('id', 'in', author_products.ids)]
            tag_domain = [('product_tag_ids.name', 'ilike', search)]
            isbn_domain = [('id', 'in', matching_templates_ids)]

            additional_domains = expression.OR([isbn_domain, author_domain, tag_domain])
            domains = expression.OR([domains, additional_domains])

            # Debugging
            pprint.pprint(domains)

            Product = request.env['product.template'].with_context(bin_size=True)
            products = Product.search(domains)

            pprint.pprint(products)

        return domains
