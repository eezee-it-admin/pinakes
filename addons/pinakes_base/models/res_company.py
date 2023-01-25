# Copyright 2021      Eezee-IT (<http://www.eezee-it.com>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
from odoo import fields, models


class Company(models.Model):
    _inherit = 'res.company'

    company_code = fields.Selection([
        ('pinakes', 'Pinakes'), ('asp', 'ASP'), ('politeia', 'Politeia')
    ], help="Technical field to identify the company to show/hide the fields.")
