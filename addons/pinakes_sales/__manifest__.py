# Copyright 2023 Eezee-IT (<http://www.eezee-it.com>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
{
    'name': 'Pinakes Sale',
    'version': '16.0.0.0.5',
    'author': 'Eezee-It',
    'category': 'Sale',
    'license': 'LGPL-3',
    'depends': [
        'sale_subscription',
        'pinakes_base'
    ],
    'data': [
        'data/template_avent_sale.xml'
        'data/server_action.xml',
        'views/sale_order.xml',
        'views/sale_order_recurrence.xml',
        'views/payment_templates.xml',
        'report/sale_report.xml',
    ],
}
