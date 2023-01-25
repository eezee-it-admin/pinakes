# Copyright 2021      Eezee-IT (<http://www.eezee-it.com>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
import json
from lxml import etree

from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    publication_type_id = fields.Many2many('publication.type')
    product_type_id = fields.Many2one('product.type', 'Type')
    imprint_id = fields.Many2one('product.imprint')
    isbn = fields.Char('ISBN')
    issn = fields.Char('ISSN')
    doi = fields.Char('DOI')
    company_code = fields.Selection([
        ('pinakes', 'Pinakes'), ('asp', 'ASP'), ('politeia', 'Politeia')
    ], compute='_compute_company_code')

    def _compute_company_code(self):
        company_code = self.env.company.company_code
        for prod in self:
            prod.company_code = company_code

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

    @api.model
    def fields_view_get(
            self, view_id=None, view_type='form', toolbar=False, submenu=False
    ):
        result = super(ProductTemplate, self).fields_view_get(
            view_id, view_type, toolbar=toolbar, submenu=submenu)
        if view_type != 'form':
            return result
        doc = etree.XML(result['arch'])
        # ASP company fields
        ASP_FIELDS = ['publication_type_id', 'imprint_id']
        for asp_field in ASP_FIELDS:
            node = doc.xpath("//field[@name='" + asp_field + "']")[0]
            modifiers = json.loads(node.get("modifiers", '{}'))
            modifiers.update({
                'invisible': [('company_code', '!=', 'asp')]
            })
            node.set("modifiers", json.dumps(modifiers))
        result['arch'] = etree.tostring(doc)
        return result


class ProductProduct(models.Model):
    _inherit = 'product.product'

    isbn = fields.Char('ISBN')
    issn = fields.Char('ISSN')
    doi = fields.Char('DOI')

    @api.model
    def fields_view_get(
            self, view_id=None, view_type='form', toolbar=False, submenu=False
    ):
        result = super(ProductProduct, self).fields_view_get(
            view_id, view_type, toolbar=toolbar, submenu=submenu)
        if view_type != 'form':
            return result
        doc = etree.XML(result['arch'])
        # ASP company fields
        FIELDS = ['isbn', 'issn', 'doi']
        for custom_field in FIELDS:
            node = doc.xpath("//field[@name='" + custom_field + "']")[0]
            modifiers = json.loads(node.get("modifiers", '{}'))
            modifiers.update({
                'invisible': [('company_code', '=', 'pinakes')]
            })
            node.set("modifiers", json.dumps(modifiers))
        result['arch'] = etree.tostring(doc)
        return result


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
