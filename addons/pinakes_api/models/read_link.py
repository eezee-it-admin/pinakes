from odoo import models, fields


class ReadLink(models.Model):
    _name = "read.link"

    sale_order_id = fields.Many2one('sale.order')
    read_link = fields.Char()
