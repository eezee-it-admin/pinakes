# -*- coding: utf-8 -*-
# Copyright 2023 Eezee-IT (<http://www.eezee-it.com>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class MailTemplate(models.Model):
    _inherit = "mail.template"

    default_template = fields.Boolean('Set Default', default=False,
                                      help="Set the template as a default.")
