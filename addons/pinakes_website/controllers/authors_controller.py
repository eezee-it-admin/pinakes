# Copyright 2023      Eezee-IT (<http://www.eezee-it.com>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import http
from odoo.http import request
from odoo.tools.translate import _


class WebsiteAuthors(http.Controller):
    @http.route(['/authors', '/authors/page/<int:page>'], type='http', auth="public", website=True)
    def authors(self, page=0, **post):
        partner_obj = request.env['res.partner']
        grade_obj = request.env['res.partner.grade']

        # Fetching the grade record for 'author' or 'auteur'
        grade = grade_obj.search([('name', 'ilike', 'author')], limit=1)
        if not grade:
            grade = grade_obj.search([('name', 'ilike', 'auteur')], limit=1)

        # Base domain for partners
        base_partner_domain = [('website_published', '=', True)]
        if grade:
            base_partner_domain += [('grade_id', '=', grade.id)]

        # Search partners matching the criteria
        partner_count = partner_obj.sudo().search_count(base_partner_domain)
        pager = request.website.pager(
            url='/authors', total=partner_count, page=page, step=20, scope=7, url_args=post)

        partner_ids = partner_obj.sudo().search(
            base_partner_domain, order="display_name ASC",
            offset=pager['offset'], limit=pager['limit'])
        partners = partner_ids.sudo()

        values = {
            'partners': partners,
            'pager': pager,
            'grade': grade,
        }
        return request.render("pinakes_website.template_authors_page", values)
