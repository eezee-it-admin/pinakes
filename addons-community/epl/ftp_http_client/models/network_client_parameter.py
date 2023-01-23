# Copyright 2017-2023 Eezee-IT (<https://www.eezee-it.com>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models, _


class NetworkClientParameter(models.Model):
    _name = 'network.client.parameter'
    _description = "Network Client Parameter"

    name = fields.Char(required=True)
    value = fields.Char()
    client_line_id = fields.Many2one(
        'network.client.line',
        string="Network Client Line",
        required=True,
        ondelete='cascade')

    _sql_constraints = [
        ('constraint_unique_parameter', 'unique(client_line_id, name)',
         _('This parameter name already exist')),
    ]
