# Copyright 2023  Eezee-IT (<http://www.eezee-it.com>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
{
    "name": "Pinakes Website",
    "version": "16.0.0.0.12",
    "author": "Eezee-It",
    "category": "Website",
    "license": "LGPL-3",
    "summary": "Pinakes Website",
    "depends": [
        "website",
        "product",
        "pinakes_base",
        "website_sale",
        "website_sale_wishlist",
    ],
    "data": [
        # Views
        "views/website_partner_templates.xml",
        "views/website_templates.xml",
        "views/snippets/s_dynamic_snippet_products.xml",

        # Templates
        "templates/wsale_product.xml",
        "templates/web_contact.xml",
    ],
    'assets': {
        'web.assets_frontend': [
            'pinakes_website/static/src/js/publication_redirect.js',
            'pinakes_website/static/src/js/tag_filters_checkboxed.js',
            'pinakes_website/static/src/js/website_reseller_template.js',
            'pinakes_website/static/src/js/hide_searchbar.js',
            'pinakes_website/static/src/js/reeds_besteld_message.js',
            'pinakes_website/static/src/scss/hide_searchbar.scss',
            'pinakes_website/static/src/js/variant_mixin.js',
            'pinakes_website/static/src/scss/hide_not_orderable.scss',
            'pinakes_website/static/src/scss/website_sale.scss'
        ],
        'website.assets_wysiwyg': [
            'pinakes_website/static/src/snippets/s_dynamic_snippet_products/options.js'
        ],
    },
    "application": False,
    "installable": True,
}
