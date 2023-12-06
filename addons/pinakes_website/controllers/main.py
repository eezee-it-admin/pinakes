# Copyright 2023      Eezee-IT (<http://www.eezee-it.com>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
from odoo import http
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale

import pprint


class CustomShopController(WebsiteSale):
    @http.route()
    def shop(self, page=0, category=None, search='', min_price=0.0, max_price=0.0, ppg=False, **post):

        website = request.env["website"].get_current_website()

        response = super(CustomShopController, self).shop(page, category, search, min_price, max_price, ppg, **post)

        tag_ids = post.get('tag')
        pprint.pprint(tag_ids)
        if tag_ids:
            tag_ids = [int(tag_id) for tag_id in tag_ids.split(',')]

            domain = self._get_search_domain(search, category, post.get('attrib_list', []))
            domain += [('product_tag_ids', 'in', tag_ids)]
            pprint.pprint(domain)

            Product = request.env['product.template']
            products = Product.search(domain)
            pprint.pprint(products)

            response.qcontext['products'] = products

            ppg = ppg if isinstance(ppg, int) and ppg > 0 else (website.shop_ppg or 20)
            response.qcontext['pager'].update(total=len(products), page_count=max(1, len(products) // ppg))

        return response
