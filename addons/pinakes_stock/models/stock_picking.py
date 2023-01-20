# Copyright 2023 Eezee-IT (<https://www.eezee-it.com>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

import logging
from odoo import fields, models

_logger = logging.getLogger(__name__)


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    auto_exported = fields.Boolean()
    auto_sent_time = fields.Datetime()
