# Copyright 2023 Eezee-IT (<https://www.eezee-it.com>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

{
    "name": "Pinakes stock",
    "version": '15.0.1.0.0',
    "application": False,
    "license": 'LGPL-3',
    "category": 'Stock',
    "summary": """Pinakes stock""",
    "author": "Eezee-It",
    "support": "support@eezee-it.com",
    "website": 'https://www.eezee-it.com',
    "depends": [
        'stock'
    ],
    "data": [
        'security/ir.model.access.csv',
        'views/stock_picking.xml',
    ],
    "external_dependencies": {},
    "demo": [],
    "qweb": [],
    "post_load": None,
    "pre_init_hook": None,
    "post_init_hook": None,
    "uninstall_hook": None,
    "auto_install": False,
    "installable": True,
}
