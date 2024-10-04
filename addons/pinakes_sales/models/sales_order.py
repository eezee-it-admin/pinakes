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
        return True

    """We need to remove the section line[Order subscriptions recurrence line]
        because the invoice does not require it. We have already
        completed the product line, so there is no need for an
        additional line for the invoice or report"""
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

    def _find_mail_template(self):
        all_events = all(line.product_id.detailed_type == 'event' for line in self.order_line)
        if all_events:
            return self.env.ref('pinakes_sales.email_template_avent_sale', raise_if_not_found=False)
        else:
            return super(SaleOrder, self)._find_mail_template()

    def get_registration_event(self):
        sale_orders_data = self.env['event.registration'].search(
            [('sale_order_id', 'in', self.ids),
             ('state', '!=', 'cancel')]
        )
        return sale_orders_data
