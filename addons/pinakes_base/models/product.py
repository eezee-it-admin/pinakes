# Copyright 2021      Eezee-IT (<http://www.eezee-it.com>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    publication_type_id = fields.Many2many('publication.type')
    organization_id = fields.Many2one('product.organization')
    product_type_id = fields.Many2one('product.type', 'Type')
    imprint_id = fields.Many2one('product.imprint')
    isbn = fields.Char('ISBN')
    issn = fields.Char('ISSN')
    doi = fields.Char('DOI')

    def action_view_authors(self):
        self.ensure_one()
        action = self.env.ref(
            "pinakes_base.action_politeia_product_author"
        ).read([])[0]
        action['domain'] = [('product_tmpl_id', 'in', self.ids)]
        action['context'] = {
            'default_product_tmpl_id': self.id,
        }
        return action


class PublicationType(models.Model):
    _name = 'publication.type'
    _description = 'Publication Type'

    name = fields.Char(required=True, translate=True)


class ProductOrganization(models.Model):
    _name = 'product.organization'
    _description = 'Organization'

    name = fields.Char(required=True, translate=True)


class ProductType(models.Model):
    _name = 'product.type'
    _description = 'Type'

    name = fields.Char(required=True, translate=True)


class ProductImprint(models.Model):
    _name = 'product.imprint'
    _description = 'Imprint'

    name = fields.Char(required=True, translate=True)
