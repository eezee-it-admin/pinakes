# Copyright 2023 Eezee-IT (<http://www.eezee-it.com>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import models, fields


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    auto_exported = fields.Boolean()
    auto_sent_time = fields.Datetime()

    def _send_order_confirmation_mail(self):
        so_template = self.sale_order_template_id
        if so_template and so_template.mail_template_id:
            return
        return super(SaleOrder, self)._send_order_confirmation_mail()

    def action_automate_weborders(self):
        for order in self:
            # Confirm the sales order
            order.action_confirm()
            # Create invoice
            order.create_and_validate_invoice()
        return True

    def create_and_validate_invoice(self):
        """Create invoice based on delivered qty"""
        wiz_inv = self.env["sale.advance.payment.inv"].create({})
        wiz_inv.with_context(
            active_ids=self.ids, active_model="sale.order"
        ).create_invoices()
        # Validate the invoice
#        self.invoice_ids.with_company(self.company_id).action_post()
        return True
