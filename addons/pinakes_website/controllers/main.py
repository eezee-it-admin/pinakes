# Copyright 2023      Eezee-IT (<http://www.eezee-it.com>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
from odoo.addons.website_sale.controllers.main import WebsiteSale


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
