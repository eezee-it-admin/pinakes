# Copyright 2023 Eezee-IT (<http://www.eezee-it.com>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
{
    "name": "Pinakes Sync",
    "version": '16.0.0.0.3',
    "application": False,
    "license": 'LGPL-3',
    "category": 'Tools',
    "summary": """
    Pinakes Sync
    """,
    "author": "Eezee-It",
    "support": "support@eezee-it.com",
    "website": 'http://www.eezee-it.com',
    "depends": [
        'base',
        'sale',
        'stock',
        'ftp_http_client',
        ],
    "external_dependencies": {
        'python': [
            'pandas',
        ],
    },
    "data": [
        'data/sync_data.xml',
    ],
    "demo": [],
    "qweb": [],
    "post_load": None,
    "pre_init_hook": None,
    "post_init_hook": None,
    "uninstall_hook": None,
    "auto_install": False,
    "installable": True,
}
