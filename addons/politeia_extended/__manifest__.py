# Copyright 2021 Eezee-IT (<http://www.eezee-it.com>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
{
    "name": "Politeia Customization",
    "version": "15.0.1.0.0",
    "author": "Eezee-It",
    "category": "Services",
    "license": "LGPL-3",
    "summary": "Politeia Customization",
    "depends": [
        "contacts",
        "product",
        "l10n_be",
    ],
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "views/product_view.xml",
        "views/product_author_view.xml",
    ],
    "application": True,
}
