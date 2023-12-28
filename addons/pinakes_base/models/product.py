# Copyright 2023 Eezee-IT (<http://www.eezee-it.com>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

import json
from lxml import etree

from odoo import api, fields, models

ACCOUNT_DOMAIN = "['&', '&', '&', ('deprecated', '=', False), " \
                 "('account_type', 'not in', ('asset_receivable', " \
                 "'liability_payable', 'asset_cash', " \
                 "'liability_credit_card')), " \
                 "('company_id', '=', current_company_id), " \
                 "('is_off_balance', '=', False)]"

PRODUCT_TYPES = [
    ('consu', 'Consumable'),
    ('service', 'Service'),
    ('product', 'Storable Product'),
    ('event', 'Event Ticket')
]


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    publication_type_id = fields.Many2many('publication.type')
    product_type_id = fields.Many2one('product.type', 'Type of Product')
    imprint_id = fields.Many2one('product.imprint')
    fonds_id = fields.Many2one('product.fonds')
    subtype_id = fields.Many2one('product.subtype', 'Subtype')
    isbn = fields.Char('ISBN')
    issn = fields.Char('ISSN')
    doi = fields.Char('DOI')
    company_code = fields.Selection([
        ('pinakes', 'Pinakes'), ('asp', 'ASP'), ('politeia', 'Politeia')
    ], compute='_compute_company_code')
    release_date = fields.Date()
    publication_lang = fields.Many2many(
        'publication.lang', 'product_template_publication_lang_rel',
        'product_id', 'lang_id', 'Publication Language'
    )
    parent_abonnement_product_id = fields.Many2one('product.template',
                                                   'Abonnement')
    abonnement_product_count = fields.Integer('Linked Subscription Products',
                                              compute='_compute_linked_products')

    product_author_ids = fields.One2many('product.author', 'product_tmpl_id')
    product_author_names = fields.Char(
        compute='_compute_product_author_names',
        help="Computed field used for the website search by the author.",
        store=True
    )
    is_visible_authors = fields.One2many(
        'product.author',
        compute='_compute_is_visible_authors'
    )
    summary = fields.Html(help="this field should be used as the summary of a book")
    is_orderable = fields.Boolean(default=True)

    @api.depends('product_author_ids.partner_id.name')
    def _compute_product_author_names(self):
        for record in self:
            record.product_author_names = ", ".join(
                record.product_author_ids.mapped('partner_id').mapped('name'))

    @api.depends('product_author_ids.partner_id.name', 'product_author_ids.is_visible')
    def _compute_is_visible_authors(self):
        for record in self:
            record.is_visible_authors = record.product_author_ids.filtered(lambda pa: pa.is_visible)

    def _compute_linked_products(self):
        for rec in self:
            rec.abonnement_product_count = self.env['product.template']. \
                search_count([('parent_abonnement_product_id', '=', rec.id)])

    def _set_account(self, vals):
        if vals.get('fonds_id'):
            founds_id = self.env['product.fonds'].browse(vals.get('fonds_id'))
            if founds_id and (founds_id.income_account_id or founds_id.expense_account_id):
                vals.update({'property_account_income_id': founds_id.income_account_id.id,
                             'property_account_expense_id': founds_id.expense_account_id.id})
        return vals

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            self._set_account(vals)
        return super().create(vals_list)

    def write(self, vals):
        self._set_account(vals)
        return super().write(vals)

    def _compute_company_code(self):
        company_code = self.env.company.company_code
        for prod in self:
            prod.company_code = company_code

    def action_view_authors(self):
        self.ensure_one()
        return {
            'name': 'Product Authors',
            'type': 'ir.actions.act_window',
            'res_model': 'product.author',
            'view_mode': 'tree',
            'domain': [('product_tmpl_id', 'in', self.ids)],
            'context': {'default_product_tmpl_id': self.id},
        }

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
        # POLITEIA company fields
        POLITEIA_FIELDS = ['fonds_id', 'subtype_id']
        for pol_field in POLITEIA_FIELDS:
            node = doc.xpath("//field[@name='" + pol_field + "']")[0]
            modifiers = json.loads(node.get("modifiers", '{}'))
            modifiers.update({
                'invisible': [('company_code', '!=', 'politeia')]
            })
            node.set("modifiers", json.dumps(modifiers))
        result['arch'] = etree.tostring(doc)
        return result


class ProductProduct(models.Model):
    _inherit = 'product.product'

    isbn = fields.Char('ISBN')
    issn = fields.Char('ISSN')
    doi = fields.Char('DOI')
    publication_lang = fields.Many2many(
        'publication.lang', 'product_product_publication_lang_rel',
        'product_id', 'lang_id', 'Publication Language'
    )
    detailed_type = fields.Selection(PRODUCT_TYPES, store=True, string='Product Type',
                                     compute='_compute_product_variant_type',
                                     inverse='_inverse_product_variant_type')
    type = fields.Selection(PRODUCT_TYPES, store=True,
                            compute='_compute_product_variant_type',
                            inverse='_inverse_product_variant_type')

    def _get_isbn(self):
        """Return the ISBN of the product variant."""
        self.ensure_one()
        return self.isbn

    @api.depends('product_tmpl_id.detailed_type')
    def _compute_product_variant_type(self):
        for product in self:
            product.detailed_type = product.product_tmpl_id.detailed_type
            product.type = product.product_tmpl_id.type

    def _inverse_product_variant_type(self):
        return

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


class ProductType(models.Model):
    _name = 'product.type'
    _description = 'Type'

    name = fields.Char(required=True, translate=True)


class ProductImprint(models.Model):
    _name = 'product.imprint'
    _description = 'Imprint'

    name = fields.Char(required=True, translate=True)


class ProductFonds(models.Model):
    _name = 'product.fonds'
    _description = 'Product Fonds'

    name = fields.Char(required=True, translate=True)
    income_account_id = fields.Many2one('account.account',
                                        company_dependent=True,
                                        string="Income Account",
                                        domain=ACCOUNT_DOMAIN)
    expense_account_id = fields.Many2one('account.account',
                                         company_dependent=True,
                                         string="Expense Account",
                                         domain=ACCOUNT_DOMAIN)

    def write(self, vals):
        if self and (vals.get('income_account_id')
                     or vals.get('expense_account_id')):
            for rec in self:
                product_ids = self.env['product.template'] \
                    .search([('fonds_id', '=', rec.id)])
                if product_ids:
                    product_ids.write({
                        'property_account_income_id':
                            vals.get('income_account_id') or False,
                        'property_account_expense_id':
                            vals.get('expense_account_id') or False
                    })
        return super().write(vals)


class ProductSubtype(models.Model):
    _name = 'product.subtype'
    _description = 'Product Subtype'

    name = fields.Char(required=True, translate=True)
