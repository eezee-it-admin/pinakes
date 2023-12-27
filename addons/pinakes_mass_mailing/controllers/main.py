from odoo import http


class MyController(http.Controller):
    @http.route('/unsubscribe_from_list', type='http', auth='public')
    def my_route(self, **kw):
        kw['request'] = http.request
        company_id = kw['request'].params.get('company')
        return http.request.render('pinakes_mass_mailing.template_mass_mailing_unsubscribe', {'company_id': company_id})
