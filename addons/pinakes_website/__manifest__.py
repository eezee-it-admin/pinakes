# Copyright 2023      Eezee-IT (<http://www.eezee-it.com>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
{
    "name": "Pinakes Website",
    "version": "16.0.0.0.2",
    "author": "Eezee-It",
    "category": "Website",
    "license": "LGPL-3",
    "summary": "Pinakes Website",
    "depends": [
        "website",
        "website_partner",
        "pinakes_base",
        "website_crm_partner_assign",
    ],
    "data": [
        "views/website_partner_templates.xml",
    ],
    'assets': {
        'web.assets_frontend': [
            'pinakes_website/static/src/js/publication_redirect.js',
        ],
    },
    "application": False,
    "installable": True,
}
