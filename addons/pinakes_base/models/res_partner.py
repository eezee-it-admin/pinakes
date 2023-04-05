# Copyright 2021      Eezee-IT (<http://www.eezee-it.com>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
from odoo import fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    vat_registered = fields.Boolean('VAT-registered')
