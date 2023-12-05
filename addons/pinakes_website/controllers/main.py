# Copyright 2023      Eezee-IT (<http://www.eezee-it.com>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
from odoo import http
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale


class WebsiteSaleInherited(WebsiteSale):

    @http.route([
        '/shop/tag/<model("product.tag"):tag>',
        '/shop/tag/<model("product.tag"):tag>/page/<int:page>',
    ], type='http', auth="public", website=True)
    def shop_tag(self, tag, page=0, **post):
        # Call the original shop method
        response = super(WebsiteSaleInherited, self).shop(page=page, category=None, search='', **post)

        # Get the current website's company ID
        current_website_company_id = request.env['website'].get_current_website().company_id.id

        # Extend the domain with the tag filter and company filter
        tag_domain = [('product_tag_ids', 'in', [tag.id])]
        company_domain = [
            '|',
            ('company_id', '=', False),
            ('company_id', '=', current_website_company_id)
        ]
        domain = response.qcontext.get('domain', []) + tag_domain + company_domain

        # Fetch products based on the updated domain
        Product = request.env['product.template'].with_context(bin_size=True)
        products = Product.search(domain)

        # Update the response context with the filtered products
        response.qcontext.update({
            'products': products,
            'search_count': len(products),  # Update the product count
        })

        # Update the pager's URL for tag-based pagination
        if 'pager' in response.qcontext:
            pager = response.qcontext['pager']
            pager['url'] = "/shop/tag/%s" % tag.id
            response.qcontext['pager'] = pager

        return response

# from odoo import http
# from odoo.http import request
#
#
# class WebsiteSale(http.Controller):
#
#     @http.route(['/shop/tag/<model("product.tag"):tag>'], type='http', auth="public", website=True)
#     def shop_tag(self, tag, **post):
#         domain = [('product_tag_ids', 'in', tag.id)]
#         products = request.env['product.template'].search(domain)
#
#         return request.render("website_sale.products_with_tag", {'products': products, 'tag': tag})
