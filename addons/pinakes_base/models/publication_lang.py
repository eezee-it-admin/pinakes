# Copyright 2021      Eezee-IT (<http://www.eezee-it.com>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
from odoo import fields, models


class PublicationLang(models.Model):
    _name = 'publication.lang'
    _description = 'Publication Lang'

    name = fields.Char(required=True)
