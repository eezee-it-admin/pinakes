# Copyright 2021-2023 Eezee-IT (<http://www.eezee-it.com>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

{
    'name': 'Automatic Export',
    'summary': "Generate a file that can be send to other application.",
    'version': '15.0.0.1.2',
    'author': "Eezee-It",
    'license': "AGPL-3",
    'category': 'Extra Tools',
    'website': 'https://eezee-it.com',
    'depends': [
        'base',
        'mail',
        'ftp_http_client',
        'sale'
    ],
    'data': [
        'data/ir_cron.xml',
        'data/template_mail.xml',
        'views/export_config_view.xml',
        'security/ir.model.access.csv'
    ],
}
