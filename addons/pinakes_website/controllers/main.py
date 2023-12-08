# Copyright 2023      Eezee-IT (<http://www.eezee-it.com>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
from odoo import http
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.osv import expression

import pprint


class CustomShopController(WebsiteSale):

    def _get_search_domain(self, search, category, attrib_values, search_in_description=True):
        domains = [request.website.sale_product_domain()]
        search_type = request.httprequest.args.get('search_type')

        if search:
            for srch in search.split(" "):
                subdomains = [
                    [('name', 'ilike', srch)],
                    [('product_variant_ids.default_code', 'ilike', srch)],
                    [('product_variant_ids.isbn', 'ilike', srch)]
                ]
                if search_in_description:
                    subdomains.append([('website_description', 'ilike', srch)])
                    subdomains.append([('description_sale', 'ilike', srch)])

                # if search_type == 'products_only':
                #     matching_variants = self.env['product.product'].search([('isbn', 'ilike', srch)])
                #     matching_templates_ids = matching_variants.mapped('product_tmpl_id').ids
                #     author_products = self.env['product.author'].search([('partner_id.name', 'ilike', srch)]).mapped(
                #         'product_tmpl_id')
                #
                #     matching_isbn_domain = [('id', 'in', matching_templates_ids)]
                #     matching_author_domain = [('id', 'in', author_products.ids)]
                #     tag_domain = [('product_tag_ids.name', 'ilike', srch)]
                #
                #     subdomains.append(matching_isbn_domain)
                #     subdomains.append(matching_author_domain)
                #     subdomains.append(tag_domain)

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

        pprint.pprint(domains)
        pprint.pprint(request.env["product.template"].search(expression.AND(domains)))

        return expression.AND(domains)

# from odoo import http
# from odoo.http import request
# from odoo.addons.website_sale.controllers.main import WebsiteSale
# from odoo.osv import expression
#
#
# class CustomShopController(WebsiteSale):
#     @http.route()  # Use appropriate route decorators as required
#     def _get_search_domain(self, search, category, attrib_values, search_in_description=True):
#         # Call the super method to get the base domain
#         domains = super(CustomShopController, self)._get_search_domain(search, category, attrib_values,
#                                                                        search_in_description)
#
#         # Your custom logic
#         search_type = request.httprequest.args.get('search_type')
#         if search_type == 'products_only' and search:
#             matching_variants = self.env['product.product'].search([('isbn', 'ilike', search)])
#             matching_templates_ids = matching_variants.mapped('product_tmpl_id').ids
#             author_products = self.env['product.author'].search([('partner_id.name', 'ilike', search)]).mapped(
#                 'product_tmpl_id')
#             tag_domain = [('product_tag_ids.name', 'ilike', search)]
#
#             # Create a custom domain
#             custom_domain = expression.OR([
#                 [('id', 'in', matching_templates_ids)],
#                 [('id', 'in', author_products.ids)],
#                 tag_domain
#             ])
#
#             # Integrate the custom domain into the existing domain logic
#             domains.append(custom_domain)
#
#         return expression.AND(domains)
