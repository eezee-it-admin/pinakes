# Copyright 2023 Eezee-IT (<http://www.eezee-it.com>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
{
    "name": "Pinakes API",
    "version": "16.0.0.0.1",
    "author": "Eezee-It",
    "category": "Services",
    "license": "LGPL-3",
    "summary": "Pinakes API",
    "depends": [
        "base",
        "sale",
        "website_sale",

        "pinakes_mass_mailing",
    ],
    'data': [
        # views
        'views/product_template_view.xml',

        #security
        'security/ir.model.access.csv',
    ],
    'external_dependencies': {
        'python': ['requests_toolbelt'],
    },
    "application": False,
}
