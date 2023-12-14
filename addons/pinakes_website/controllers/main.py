# Copyright 2023      Eezee-IT (<http://www.eezee-it.com>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
from odoo import http
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.osv import expression


class CustomShopController(WebsiteSale):
    def _get_search_options(
        self, category=None, attrib_values=None, pricelist=None,
        min_price=0.0, max_price=0.0, conversion_rate=1, **post
    ):
        options = super(CustomShopController, self)._get_search_options(
            category, attrib_values, pricelist, min_price, max_price,
            conversion_rate, **post
        )

        tag_ids = post.get('tag')

        if tag_ids:
            options['product_tag_ids'] = [int(tag_id) for tag_id in tag_ids.split(',')]

        return options

    def _get_search_domain(self, search, category, attrib_values, search_in_description=True):
        """Inherited from Odoo: only used for the filter by price."""
        domains = [request.website.sale_product_domain()]
        if search:
            for srch in search.split(" "):
                subdomains = [
                    [('name', 'ilike', srch)],
                    [('product_variant_ids.default_code', 'ilike', srch)],
                    [('product_variant_ids.isbn', 'ilike', srch)],
                    [('product_author_names', 'ilike', srch)],
                ]
                if search_in_description:
                    subdomains.append([('website_description', 'ilike', srch)])
                    subdomains.append([('description_sale', 'ilike', srch)])
                domains.append(expression.OR(subdomains))

        if category:
            domains.append([('public_categ_ids', 'child_of', int(category))])

        if attrib_values:
            attrib = None
            ids = []
            for value in attrib_values:
                if not attrib:
                    attrib = value[0]
                    ids.append(value[1])
                elif value[0] == attrib:
                    ids.append(value[1])
                else:
                    domains.append([('attribute_line_ids.value_ids', 'in', ids)])
                    attrib = value[0]
                    ids = [value[1]]
            if attrib:
                domains.append([('attribute_line_ids.value_ids', 'in', ids)])

        return expression.AND(domains)