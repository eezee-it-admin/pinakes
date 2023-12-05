# Copyright 2023      Eezee-IT (<http://www.eezee-it.com>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
from odoo import http
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.http import request


class CustomShopController(WebsiteSale):
    @http.route()
    def shop(self, page=0, category=None, search='', min_price=0.0, max_price=0.0, ppg=False, tag=None, **post):
        # Call super to keep existing functionality
        response = super(CustomShopController, self).shop(
            page=page,
            category=category,
            search=search,
            min_price=min_price,
            max_price=max_price,
            ppg=ppg,
            **post
        )

        # Additional tag filtering logic
        if tag:
            tag_ids = [int(tid) for tid in tag.split(',')]
            domain = [('product_tag_ids', 'in', tag_ids)]
            Product = request.env['product.template']
            products = Product.search(domain)
            response.qcontext['products'] = products

        return response
