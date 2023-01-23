# Copyright 2021      Eezee-IT (<http://www.eezee-it.com>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
from odoo import fields, models


class ProductAuthor(models.Model):
    _name = 'product.author'
    _description = 'Product Authors'

    product_tmpl_id = fields.Many2one(
        'product.template', 'Product', required=True
    )
    partner_id = fields.Many2one(
        'res.partner', string='Author', required=True
    )
    company_id = fields.Many2one(
        'res.company', 'Company', readonly=True,
        default=lambda x: x.env.company,
    )
    currency_id = fields.Many2one(
        'res.currency', 'Currency', related='company_id.currency_id',
        store=True
    )
    royalty_perc = fields.Float('Royalty (%)')
    page_price_royalty = fields.Monetary()
    forfait_price = fields.Monetary()
