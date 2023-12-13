# Copyright 2023  Eezee-IT (<http://www.eezee-it.com>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
{
    "name": "Pinakes Website",
    "version": "16.0.0.0.3",
    "author": "Eezee-It",
    "category": "Website",
    "license": "LGPL-3",
    "summary": "Pinakes Website",
    "depends": [
        "website",
        "product",
        "pinakes_base",
        "website_crm_partner_assign",
        "website_sale",
        "website_sale_wishlist",
    ],
    "data": [
        "views/website_templates.xml",
        "views/website_crm_partner_assign_templates.xml",
        "templates/wsale_product.xml",
    ],
    'assets': {
        'web.assets_frontend': [
            'pinakes_website/static/src/js/publication_redirect.js',
            'pinakes_website/static/src/js/tag_filters_checkboxed.js',
            'pinakes_website/static/src/js/website_reseller_template.js',
        ],
    },
    "application": False,
    "installable": True,
}
