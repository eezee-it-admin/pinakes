# -*- coding: utf-8 -*-
# Copyright 2023 Eezee-IT (<http://www.eezee-it.com>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import models


class AccountMove(models.Model):
    _inherit = "account.move"

    # Inherited to select default email template
    def _get_mail_template(self):
        if not all(move.move_type == 'out_refund' for move in self):
            email_template = self.env['mail.template'].search(
                [('default_template', '=', True)])
            if email_template:
                return email_template.get_external_id().get(email_template.id)
            else:
                return super()._get_mail_template()
        else:
            return super()._get_mail_template()
