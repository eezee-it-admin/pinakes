# Copyright 2023 Eezee-IT (<http://www.eezee-it.com>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class SaleReport(models.Model):
    _inherit = "sale.report"

    # publication_type_id = fields.Many2many('publication.type')
    product_type_id = fields.Many2one('product.type', 'Type of Product')
    imprint_id = fields.Many2one('product.imprint')
    fonds_id = fields.Many2one('product.fonds')
    subtype_id = fields.Many2one('product.subtype', 'Subtype')

    def _select_additional_fields(self):
        res = super()._select_additional_fields()
        # res['publication_type_id'] = "pub.publication_type_id"
        res['product_type_id'] = "t.product_type_id"
        res['imprint_id'] = 't.imprint_id'
        res['fonds_id'] = 't.fonds_id'
        res['subtype_id'] = "t.subtype_id"
        return res

    # def _from_sale(self):
    #     res = super()._from_sale()
    #     res += """
    #         LEFT JOIN product_template_publication_type_rel pub ON pub.product_template_id = t.id
    #     """
    #     return res

    def _group_by_sale(self):
        res = super()._group_by_sale()
        res += """,
            t.product_type_id,t.imprint_id,
            t.fonds_id,t.subtype_id"""
        # pub.publication_type_id,
        return res
