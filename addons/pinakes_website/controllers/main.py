# Copyright 2023      Eezee-IT (<http://www.eezee-it.com>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
from odoo import http
from odoo.http import request
from odoo.osv import expression
from odoo.addons.website_sale.controllers.main import WebsiteSale

import pprint

from odoo import models


class CustomWebsite(models.Model):
    _inherit = 'website'

    def _search_with_fuzzy(self, search_type, search, limit, order, options):
        # Call the super method to get the standard search details
        count, results, fuzzy_term = super(CustomWebsite, self)._search_with_fuzzy(
            search_type, search, limit, order, options)

        # Only modify the search for product.template
        if search_type == 'products_only':
            # Custom domain logic
            matching_variants = self.env['product.product'].search([('isbn', 'ilike', search)])
            matching_templates_ids = matching_variants.mapped('product_tmpl_id').ids
            author_products = self.env['product.author'].search([('partner_id.name', 'ilike', search)]).mapped(
                'product_tmpl_id')
            tag_domain = [('product_tag_ids.name', 'ilike', search)]

            # Create a custom domain
            custom_domain = expression.OR([
                [('id', 'in', matching_templates_ids)],
                [('id', 'in', author_products.ids)],
                tag_domain
            ])

            # Apply the custom domain to product.template search details
            for detail in results:
                if detail['model'] == 'product.template':
                    detail['base_domain'] = expression.OR([detail['base_domain'], custom_domain])

            pprint.pprint(results)

        return count, results, fuzzy_term

    # def _search_get_details(self, search_type, order, options):
    #     search_details = super(CustomWebsite, self)._search_get_details(search_type, order, options)
    #
    #     # Custom domain logic
    #     custom_domain = []
    #     if search_type == 'products_only':
    #         search = options.get('search')
    #         pprint.pprint(search)
    #         if search:
    #             matching_variants = self.env['product.product'].search([('isbn', 'ilike', search)])
    #             matching_templates_ids = matching_variants.mapped('product_tmpl_id').ids
    #             author_products = self.env['product.author'].search([('partner_id.name', 'ilike', search)]).mapped('product_tmpl_id')
    #             custom_domain = expression.OR([
    #                 [('id', 'in', matching_templates_ids)],
    #                 [('id', 'in', author_products.ids)],
    #                 [('product_tag_ids.name', 'ilike', search)]
    #             ])
    #
    #     # Modify the base_domain for product.template
    #     for detail in search_details:
    #         if detail['model'] == 'product.template':
    #             # Only apply the custom domain if it's not empty
    #             if custom_domain:
    #                 detail['base_domain'] = expression.OR([detail['base_domain'], custom_domain])
    #
    #     return search_details


#
# from odoo import api, models
# from odoo.osv import expression
#
#
# class CustomWebsite(models.Model):
#     _inherit = 'website'

# def _search_with_fuzzy(self, search_type, search, limit, order, options):
#
#     fuzzy_term = False
#     search_details = self._search_get_details(search_type, order, options)
#     if search and options.get('allowFuzzy', True):
#         fuzzy_term = self._search_find_fuzzy_term(search_details, search)
#         if fuzzy_term:
#             count, results = self._search_exact(search_details, fuzzy_term, limit, order)
#             if fuzzy_term.lower() == search.lower():
#                 fuzzy_term = False
#         else:
#             count, results = self._search_exact(search_details, search, limit, order)
#     else:
#         count, results = self._search_exact(search_details, search, limit, order)
#     return count, results, fuzzy_term

# def _search_with_fuzzy(self, search_type, search, limit, order, options):
#     # Standard search details
#     search_details = self._search_get_details(search_type, order, options)
#
#     # Custom domain logic
#     matching_variants = self.env['product.product'].search([('isbn', 'ilike', search)])
#     matching_templates_ids = matching_variants.mapped('product_tmpl_id').ids
#     author_products = self.env['product.author'].search([('partner_id.name', 'ilike', search)]).mapped(
#         'product_tmpl_id')
#     custom_domain = expression.OR([
#         [('id', 'in', matching_templates_ids)],
#         [('id', 'in', author_products.ids)],
#         [('product_tag_ids.name', 'ilike', search)]
#     ])
#
#     # Modify search details to include custom domain
#     for detail in search_details:
#         if detail['model'] == 'product.template':
#             detail['base_domain'] = expression.OR([detail['base_domain'], custom_domain])
#
#     # Disable fuzzy search if the search input contains only digits
#     if search.isdigit():
#         options['allowFuzzy'] = False
#
#     # Call super method with modified search details
#     return super(CustomWebsite, self)._search_with_fuzzy(search_type, search, limit, order, options)


# class WebsiteSaleExtendedSearch(WebsiteSale):
#
#     def _get_search_domain(self, search, category, attrib_values, search_in_description=True):
#         # Base domains from the super method
#         domains = super(WebsiteSaleExtendedSearch, self)._get_search_domain(search, category, attrib_values,
#                                                                             search_in_description)
#
#         if search:
#             matching_variants = request.env['product.product'].search([('isbn', 'ilike', search)])
#             matching_templates_ids = matching_variants.mapped('product_tmpl_id').ids
#
#             author_products = request.env['product.author'].search([('partner_id.name', 'ilike', search)]).mapped(
#                 'product_tmpl_id')
#             author_domain = [('id', 'in', author_products.ids)]
#             tag_domain = [('product_tag_ids.name', 'ilike', search)]
#             isbn_domain = [('id', 'in', matching_templates_ids)]
#
#             additional_domains = expression.OR([isbn_domain, author_domain, tag_domain])
#             domains = expression.OR([domains, additional_domains])
#
#             # Debugging
#             # pprint.pprint(domains)
#             #
#             # Product = request.env['product.template'].with_context(bin_size=True)
#             # products = Product.search(domains)
#             #
#             # pprint.pprint(products)
#
#         return domains
