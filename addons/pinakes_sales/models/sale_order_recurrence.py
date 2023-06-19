# -*- coding: utf-8 -*-
# Copyright 2023 Eezee-IT (<http://www.eezee-it.com>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models, api


class SaleOrderRecurrence(models.Model):
    _inherit = 'sale.temporal.recurrence'

    unlimited_execution = fields.Boolean("Unlimited Recurrence",
                                         default=False, copy=False,
                                         help="Mark this to mentioned "
                                              "recurrency unlimited times.")

    @api.onchange('unlimited_execution')
    def _change_period(self):
        if self.unlimited_execution:
            self.write({
                'duration': 999,
                'unit': 'year'
            })
