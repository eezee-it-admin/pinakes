# Copyright 2023 Eezee-IT (<http://www.eezee-it.com>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
from odoo import models, fields


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    epub_file = fields.Binary()
    epub_name = fields.Char()
    url_digitale_bib = fields.Char()
    reeds_besteld = fields.Html()
