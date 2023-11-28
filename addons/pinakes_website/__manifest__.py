# Copyright 2023      Eezee-IT (<http://www.eezee-it.com>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
{
    "name": "Pinakes Website",
    "version": "16.0.0.0.0",
    "author": "Eezee-It",
    "category": "Website",
    "license": "LGPL-3",
    "summary": "Pinakes Website",
    "depends": [
        "website",
        "pinakes_base",
        "website_crm_partner_assign",
    ],
    "data": [
        "views/website_templates.xml",
        "views/website_crm_partner_assign_templates.xml"
    ],
    'assets': {
        'web.assets_frontend': [
            'pinakes_website/static/src/js/website_reseller_template.js',
        ],
    },
    "application": False,
    "installable": True,
}
