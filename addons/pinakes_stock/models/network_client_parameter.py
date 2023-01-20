# -*- coding: utf-8 -*-
# #############################################################################
#
#    Copyright Eezee-It (C) 2017-2020
#    Author: Eezee-It <info@eezee-it.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Lesser General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Lesser General Public License for more details.
#
#    You should have received a copy of the GNU Lesser General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################
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
