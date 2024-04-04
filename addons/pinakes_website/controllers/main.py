# Copyright 2023      Eezee-IT (<http://www.eezee-it.com>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
from odoo import http
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.osv import expression


class CustomShopController(WebsiteSale):
    def _get_search_options(
            self, category=None, attrib_values=None, pricelist=None,
            min_price=0.0, max_price=0.0, conversion_rate=1, **post
    ):
        options = super(CustomShopController, self)._get_search_options(
            category, attrib_values, pricelist, min_price, max_price,
            conversion_rate, **post
        )

        tag_ids = post.get('tag')

        if tag_ids:
            options['product_tag_ids'] = [int(tag_id) for tag_id in tag_ids.split(',')]

        return options

    def _get_search_domain(self, search, category, attrib_values, search_in_description=True):
        """Inherited from Odoo: only used for the filter by price."""
        domains = [request.website.sale_product_domain()]
        if search:
            for srch in search.split(" "):
                subdomains = [
                    [('name', 'ilike', srch)],
                    [('product_variant_ids.default_code', 'ilike', srch)],
                    [('product_variant_ids.isbn', 'ilike', srch)],
                    [('product_author_names', 'ilike', srch)],
                ]
                if search_in_description:
                    subdomains.append([('website_description', 'ilike', srch)])
                    subdomains.append([('description_sale', 'ilike', srch)])
                domains.append(expression.OR(subdomains))

        if category:
            domains.append([('public_categ_ids', 'child_of', int(category))])

        if attrib_values:
            attrib = None
            ids = []
            for value in attrib_values:
                if not attrib:
                    attrib = value[0]
                    ids.append(value[1])
                elif value[0] == attrib:
                    ids.append(value[1])
                else:
                    domains.append([('attribute_line_ids.value_ids', 'in', ids)])
                    attrib = value[0]
                    ids = [value[1]]
            if attrib:
                domains.append([('attribute_line_ids.value_ids', 'in', ids)])

        return expression.AND(domains)

    @http.route('/product/filter_unique', type='json', auth='user', website=True)
    def filter_unique_products(self, search_domain):
        # Effectuer la recherche des produits avec le searchDomain
        products = request.env['product.product'].search(search_domain)

        # Créer un dictionnaire pour regrouper les produits par product_tmpl_id
        product_tmpl_dict = {}
        for product in products:
            product_tmpl_id = product.product_tmpl_id.id
            if product_tmpl_id not in product_tmpl_dict:
                product_tmpl_dict[product_tmpl_id] = product.id

        # Extraire les identifiants uniques des produits
        unique_product_ids = list(product_tmpl_dict.values())

        return {'ids': unique_product_ids}

class ShopController(http.Controller):

    @http.route('/shop/check_variants', type='json', auth='public')
    def check_variants(self, product_id, **kwargs):
        # Récupérer le produit par son ID
        product = request.env['product.product'].sudo().browse(int(product_id))
        if not product:
            return {'error': 'Product not found'}

        # Récupérer tous les produits ayant le même product_tmpl_id
        products = request.env['product.product'].sudo().search(
            [('product_tmpl_id', '=', product.product_tmpl_id.id)])

        # Préparer les données pour le rendu
        product_data = []
        for product in products:
            product_data.append({
                'id': product.id,
                'name': product.display_name,
                'image_url': product.image_1920,
                # Ajoutez d'autres champs si nécessaire
            })

        # Renvoyer les données au lieu de rendre le template XML
        return {'products': product_data}
