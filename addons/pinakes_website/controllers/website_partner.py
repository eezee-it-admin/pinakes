# Copyright 2023      Eezee-IT (<http://www.eezee-it.com>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import http
from odoo.http import request
from odoo.addons.website_partner.controllers.main import WebsitePartnerPage


class CustomWebsitePartnerPage(WebsitePartnerPage):

    @http.route()
    def partners_detail(self, partner_id, **post):
        response = super(CustomWebsitePartnerPage, self).partners_detail(partner_id, **post)

        if response.qcontext.get('partner'):
            partner_sudo = response.qcontext['partner']

            # Fetch product.author records associated with this partner
            product_author_records = request.env['product.author'].search([('partner_id', '=', partner_sudo.id)])
            product_ids = product_author_records.mapped('product_tmpl_id')

            response.qcontext['publications'] = product_ids

        return response
