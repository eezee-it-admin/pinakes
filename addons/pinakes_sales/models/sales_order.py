# Copyright 2022 Eezee-IT (<http://www.eezee-it.com>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def _send_order_confirmation_mail(self):
        res = super(SaleOrder, self)._send_order_confirmation_mail()
        if self.transaction_ids:
            return res
        return
