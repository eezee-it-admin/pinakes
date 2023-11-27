# Copyright 2021      Eezee-IT (<http://www.eezee-it.com>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

import re
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class ResPartner(models.Model):
    _inherit = 'res.partner'

    vat_registered = fields.Boolean('VAT-registered')

    @api.constrains('citizen_identification')
    def _check_formation(self):
        for partner in self:
            if partner.citizen_identification and not re.match(
                    r'^\d{2}\.\d{2}\.\d{2}-\d{3}\.\d{2}$',
                    partner.citizen_identification):
                raise ValidationError(_('Please fill-in with the correct'
                                        ' format : XX.XX.XX-XXX.XX'))

    author_summary = fields.Html()
    website_short_description = fields.Html()
