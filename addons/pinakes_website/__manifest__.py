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
        "website_sale"
    ],
    "data": [
        "views/website_templates.xml",
        # "views/snippets/dynamic_snippets/s_product_public_category_tags.xml",
        # "views/snippets.xml",
        "templates/wsale_product.xml",
    ],
    "application": False,
    "installable": True,
}
