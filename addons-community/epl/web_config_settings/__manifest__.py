# Copyright 2022  Eezee-IT (<http://www.eezee-it.com>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
{
    'name': 'Web: Common EPL Settings',
    'version': '16.0.0.0.0',
    'author': 'Eezee-It',
    'category': 'Web',
    'license': 'LGPL-3',
    'depends': ['base_setup'],
    'data': [
        'templates/assets_backend.xml',
        'views/res_config_settings.xml',
    ],
    'web.assets_backend': [
        'web_config_settings/static/src/css/backend-styles.css',
        ],
    'auto_install': True
}
