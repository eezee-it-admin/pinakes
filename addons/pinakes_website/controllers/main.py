# Copyright 2023      Eezee-IT (<http://www.eezee-it.com>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
from odoo import http
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.osv import expression

import pprint

from odoo import models, fields, api
from odoo.osv import expression


class CustomWebsite(models.Model):
    _inherit = "website"

    def _search_exact(self, search_details, search, limit, order):
        all_results = []
        total_count = 0
        for search_detail in search_details:
            model = self.env[search_detail['model']]

            # Custom search logic for 'isbn' and authors
            if model._name == 'product.template':
                custom_domain = []
                if 'isbn' in model._fields:
                    custom_domain.append([('isbn', 'ilike', search)])

                # Handling product authors relation
                authors = self.env['product.author'].search([('partner_id.name', 'ilike', search)])
                product_ids = authors.mapped('product_tmpl_id.id')
                if product_ids:
                    custom_domain.append([('id', 'in', product_ids)])

                # Combine custom domain with existing domain
                if custom_domain:
                    search_detail['base_domain'] = expression.OR(
                        [search_detail['base_domain'], expression.OR(custom_domain)])

            results, count = model._search_fetch(search_detail, search, limit, order)
            search_detail['results'] = results
            total_count += count
            search_detail['count'] = count
            all_results.append(search_detail)
        return total_count, all_results

# class CustomShopController(WebsiteSale):
#
#     def _get_search_domain(self, search, category, attrib_values, search_in_description=True):
#         domains = [request.website.sale_product_domain()]
#         search_type = request.httprequest.args.get('search_type')
#
#         if search:
#             for srch in search.split(" "):
#                 subdomains = [
#                     [('name', 'ilike', srch)],
#                     [('product_variant_ids.default_code', 'ilike', srch)],
#                     [('product_variant_ids.isbn', 'ilike', srch)]
#                 ]
#                 if search_in_description:
#                     subdomains.append([('website_description', 'ilike', srch)])
#                     subdomains.append([('description_sale', 'ilike', srch)])
#
#                 # if search_type == 'products_only':
#                 #     matching_variants = self.env['product.product'].search([('isbn', 'ilike', srch)])
#                 #     matching_templates_ids = matching_variants.mapped('product_tmpl_id').ids
#                 #     author_products = self.env['product.author'].search([('partner_id.name', 'ilike', srch)]).mapped(
#                 #         'product_tmpl_id')
#                 #
#                 #     matching_isbn_domain = [('id', 'in', matching_templates_ids)]
#                 #     matching_author_domain = [('id', 'in', author_products.ids)]
#                 #     tag_domain = [('product_tag_ids.name', 'ilike', srch)]
#                 #
#                 #     subdomains.append(matching_isbn_domain)
#                 #     subdomains.append(matching_author_domain)
#                 #     subdomains.append(tag_domain)
#
#                 domains.append(expression.OR(subdomains))
#
#         pprint.pprint(subdomains)
#         pprint.pprint(request.env["product.template"].search(subdomains))
#
#         if category:
#             domains.append([('public_categ_ids', 'child_of', int(category))])
#
#         if attrib_values:
#             attrib = None
#             ids = []
#             for value in attrib_values:
#                 if not attrib:
#                     attrib = value[0]
#                     ids.append(value[1])
#                 elif value[0] == attrib:
#                     ids.append(value[1])
#                 else:
#                     domains.append([('attribute_line_ids.value_ids', 'in', ids)])
#                     attrib = value[0]
#                     ids = [value[1]]
#             if attrib:
#                 domains.append([('attribute_line_ids.value_ids', 'in', ids)])
#
#         pprint.pprint(domains)
#         pprint.pprint(request.env["product.template"].search(expression.AND(domains)))
#
#         return expression.AND(domains)

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
