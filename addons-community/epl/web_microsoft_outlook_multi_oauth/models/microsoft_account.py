# Copyright 2021 Eezee-IT (<http://www.eezee-it.com> - admin@eezee-it.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class MicrosoftAccount(models.Model):
    _name = 'microsoft.account.outlook'
    _description = 'Microsoft Account for outlook'

    name = fields.Char(required=True)
    client_id = fields.Char(required=True, string="Application Id")
    client_secret = fields.Char(required=True)
