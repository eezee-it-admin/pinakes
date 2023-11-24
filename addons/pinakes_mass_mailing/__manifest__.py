# Copyright 2021 Eezee-IT (<http://www.eezee-it.com>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
{
    'name': 'Pinakes Mass Mailing',
    'version': '16.0.0.0.1',
    'author': 'Eezee-It',
    'category': 'Mailing',
    'license': 'LGPL-3',
    'summary': 'Pinakes Mass Mailing',
    'depends': [
        'mass_mailing',
        'website',
        'mass_mailing_custom_unsubscribe',
    ],
    'data': [
        'templates/email_designer_snippets.xml',
        'templates/snippets.xml',
        'templates/unsubscription_template.xml',
    ],
    'application': True,
}
