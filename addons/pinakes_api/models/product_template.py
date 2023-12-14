# Copyright 2023 Eezee-IT (<http://www.eezee-it.com>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
from odoo import models, fields


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    epub_file = fields.Binary(string='Epub File')
    epub_name = fields.Char(string='Epub Name')
