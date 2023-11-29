# Copyright 2023      Eezee-IT (<http://www.eezee-it.com>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo.addons.website_crm_partner_assign.controllers.main import WebsiteCrmPartnerAssign

from odoo import http
from odoo.http import request


class CustomWebsiteCrmPartnerAssign(WebsiteCrmPartnerAssign):

    def partners(self, country=None, grade=None, page=0, **post):
        # Call the super method and get its output
        response = super(CustomWebsiteCrmPartnerAssign, self).partners(country, grade, page, **post)

        # Define a new base_partner_domain without the 'is_company' condition
        base_partner_domain = [('grade_id', '!=', False), ('website_published', '=', True)]
        if not request.env['res.users'].has_group('website.group_website_restricted_editor'):
            base_partner_domain += [('grade_id.website_published', '=', True)]
        if response.qcontext.get('search'):
            search = response.qcontext.get('search')
            base_partner_domain += ['|', ('name', 'ilike', search), ('website_description', 'ilike', search)]

        # Apply additional domain filters based on country and grade, if present
        if country:
            base_partner_domain += [('country_id', '=', country.id)]
        if grade:
            base_partner_domain += [('grade_id', '=', grade.id)]

        # Perform a search with the updated domain
        partner_obj = request.env['res.partner']
        partner_ids = partner_obj.sudo().search(
            base_partner_domain,
            order="grade_sequence ASC, implemented_partner_count DESC, display_name ASC, id ASC",
            offset=response.qcontext.get('pager')['offset'],
            limit=self._references_per_page
        )

        # Update the response context with the new partners list
        response.qcontext['partners'] = partner_ids

        return response
