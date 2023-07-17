# -*- coding: utf-8 -*-
# Copyright 2023 Eezee-IT (<http://www.eezee-it.com>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class AccountInvoiceReport(models.Model):
    _inherit = "account.invoice.report"

    product_type_id = fields.Many2one('product.type', 'Type of Product')
    imprint_id = fields.Many2one('product.imprint', 'Product Imprint')
    fonds_id = fields.Many2one('product.fonds', 'Product Founds')
    subtype_id = fields.Many2one('product.subtype', 'Product Subtype')

    _depends = {
        'product.template': ['product_type_id', 'imprint_id', 'fonds_id',
                             'subtype_id']
    }

    def _select(self):
        return super()._select() + \
            ", template.product_type_id as product_type_id," \
            "template.imprint_id as imprint_id, " \
            "template.fonds_id as fonds_id, " \
            "template.subtype_id as subtype_id"
