# Copyright 2017-2023 Eezee-IT (<https://www.eezee-it.com>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

{
    "name": "FTP / HTTP Client",
    "version": '16.0.0.0.1',
    "application": False,
    "license": 'LGPL-3',
    "category": 'Tools',
    "summary": """
    FTP / HTTP Client
    """,
    "author": "Eezee-It",
    "support": "support@eezee-it.com",
    "website": 'https://www.eezee-it.com',
    "depends": [
        'base'
    ],
    "data": [
        'security/ftp_security.xml',
        'security/ir.model.access.csv',
        'views/network_client.xml',
        'views/network_client_parameter.xml',
        'views/network_client_line.xml',
        'views/ir_attachment.xml',
        'views/ir_logging.xml',
        'views/menu.xml',
    ],
    "external_dependencies": {
        'python': [
            'pandas', 'pysftp'
        ],
    },
    "demo": [],
    "qweb": [],
    "post_load": None,
    "pre_init_hook": None,
    "post_init_hook": None,
    "uninstall_hook": None,
    "auto_install": False,
    "installable": True,
}
