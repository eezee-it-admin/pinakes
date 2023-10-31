# Copyright 2023 Eezee-IT (<http://www.eezee-it.com>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import models, fields


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    auto_exported = fields.Boolean()
    auto_sent_time = fields.Datetime()
    # delivery_email = fields.Char('Delivery Email', compute='_compute_delivery_email')

    # def _compute_delivery_email(self):
    #     for rec in self:
    #         email = ''
    #         rec.delivery_email = email

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

    def _get_invoiceable_lines(self, final=False):
        res = super()._get_invoiceable_lines(final=final)
        is_99 = False
        value = ['99 jaren', '99 Jaren']
        for rec in self:
            if rec.recurrence_id and\
                    rec.recurrence_id.name in value:
                is_99 = True
        if is_99:
            return res.\
                filtered(lambda x: x.display_type != 'line_note'
                         and x.sequence != '999')
        else:
            return res
