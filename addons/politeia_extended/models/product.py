# Copyright 2021      Eezee-IT (<http://www.eezee-it.com>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    publication_type_id = fields.Many2many('publication.type')
    organization_id = fields.Many2one('organization')
    type_id = fields.Many2one('type')
    imprint_id = fields.Many2one('imprint')

    def action_view_authors(self):
        self.ensure_one()
        action = self.env.ref(
            "politeia_extended.action_politeia_product_author"
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


class Organization(models.Model):
    _name = 'organization'
    _description = 'Organization'

    name = fields.Char(required=True, translate=True)


class Type(models.Model):
    _name = 'type'
    _description = 'Type'

    name = fields.Char(required=True, translate=True)


class Imprint(models.Model):
    _name = 'imprint'
    _description = 'Imprint'

    name = fields.Char(required=True, translate=True)
