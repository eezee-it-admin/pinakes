# Copyright 2021 Eezee-IT (<http://www.eezee-it.com>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
{
    'name': 'Microsoft account multi OAuth',
    'version': '16.0.0.0.1',
    'author': 'Eezee-It',
    'category': 'Hidden/Tools',
    'license': 'LGPL-3',
    'depends': [
        'microsoft_outlook',
    ],
    'data': [
        'views/microsoft_account.xml',
        'views/ir_mail_server_views.xml',
        'views/fetchmail_server.xml',
        'security/ir.model.access.csv',
    ]
}
