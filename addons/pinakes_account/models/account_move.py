# -*- coding: utf-8 -*-
# Copyright 2023 Eezee-IT (<http://www.eezee-it.com>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import models


class AccountMove(models.Model):
    _inherit = "account.move"

    # # Inherited to select default email template
    # def _get_mail_template(self):
    #     if not all(move.move_type == 'out_refund' for move in self):
    #         email_template = self.env['mail.template'].search(
    #             [('default_template', '=', True)])
    #         if email_template:
    #             return str(email_template.id) #email_template.get_external_id().get(email_template.id)
    #         else:
    #             return super()._get_mail_template()
    #     else:
    #         return super()._get_mail_template()

    def action_invoice_sent(self):
        res = super(AccountMove, self).action_invoice_sent()
        if not all(move.move_type == 'out_refund' for move in self):
            template = self.env['mail.template'].search(
                [('default_template', '=', True)], limit=1)
            if template:
                res['context'].update({'default_template_id': template.id})
        return res
