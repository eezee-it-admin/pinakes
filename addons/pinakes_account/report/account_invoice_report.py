# -*- coding: utf-8 -*-
# Copyright 2023 Eezee-IT (<http://www.eezee-it.com>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models
from datetime import date


class AccountInvoiceReport(models.Model):
    _inherit = "account.invoice.report"

    product_type_id = fields.Many2one('product.type', 'Type of Product')
    imprint_id = fields.Many2one('product.imprint', 'Product Imprint')
    fonds_id = fields.Many2one('product.fonds', 'Product Founds')
    subtype_id = fields.Many2one('product.subtype', 'Product Subtype')

    _depends = {
        'product.template': ['product_type_id', 'imprint_id', 'fonds_id',
                             'subtype_id']
    }

    def _select(self):
        return super()._select() + \
            ", template.product_type_id as product_type_id," \
            "template.imprint_id as imprint_id, " \
            "template.fonds_id as fonds_id, " \
            "template.subtype_id as subtype_id"


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    def get_line_name(self):
        source_orders = self.sale_line_ids.order_id
        source_orders = source_orders.filtered(lambda r: r.recurrence_id)
        if source_orders and source_orders[0].recurrence_id:
            current_year = source_orders[0].start_date.year
            name = self.product_id.display_name
            value = 'continuous subscription'
            if self.move_id.partner_id.lang == 'nl_BE':
                value = 'doorlopend abonnement'
            elif self.move_id.partner_id.lang == 'fr_BE':
                value = 'abonnement continu'
            # if '1 Jaar' in self.name:
            #     year_start = date(current_year, 1, 1).strftime("%d-%m-%Y")
            #     year_end = date(current_year, 12, 31).strftime("%d-%m-%Y")
            #     name += ' - \n1 jaar '
            #     name += (str(year_start) + ' t/m ' + str(year_end))
            #     return name
            # elif '1 Year' in self.name:
            #     year_start = date(current_year, 1, 1).strftime("%d-%m-%Y")
            #     year_end = date(current_year, 12, 31).strftime("%d-%m-%Y")
            #     name += ' - \n1 Year '
            #     name += (str(year_start) + ' t/m ' + str(year_end))
            #     return name
            elif '999 Jaren' in self.name:
                name += """ - \n{value}""".format(value=value)
                return name
            else:
                return self.name
        else:
            return self.name
