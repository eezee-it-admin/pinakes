# Copyright 2023      Eezee-IT (<http://www.eezee-it.com>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo.addons.website_crm_partner_assign.controllers.main import WebsiteAccount


class CustomWebsiteAccount(WebsiteAccount):

    def partners(self, country=None, grade=None, page=0, **post):
        # Call the super method and get its output
        response = super(CustomWebsiteAccount, self).partners(country, grade, page, **post)

        # Modify the base_partner_domain
        base_partner_domain = response.qcontext.get('base_partner_domain', [])
        if ('is_company', '=', True) in base_partner_domain:
            base_partner_domain.remove(('is_company', '=', True))

        # Perform a search with the updated domain or any other modifications
        partner_obj = request.env['res.partner']
        partner_ids = partner_obj.sudo().search(
            base_partner_domain,
            offset=response.qcontext.get('pager')['offset'],
            limit=self._references_per_page
        )

        # Update the response context
        response.qcontext['partners'] = partner_ids

        return response
