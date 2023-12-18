# Copyright 2023      Eezee-IT (<http://www.eezee-it.com>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
from odoo import http
from odoo.http import request
from odoo.addons.website_sale.controllers.variant import WebsiteSaleVariantController
import pprint


class CustomWebsiteSaleVariantController(WebsiteSaleVariantController):
    @http.route()
    def get_combination_info_website(self, product_template_id, product_id, combination, add_qty, **kw):
        combination_info = super(CustomWebsiteSaleVariantController, self).get_combination_info_website(
            product_template_id, product_id, combination, add_qty, **kw
        )

        product_variant = request.env['product.product'].browse(combination_info['product_id'])
        combination_info['isbn'] = product_variant and product_variant.isbn or 'N/A'
        pprint.pprint(combination_info)
        pprint.pprint(product_variant)

        return combination_info
