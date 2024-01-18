from odoo import models, fields


class BooxtreamLink(models.Model):
    _name = "ebook.link"
    _description = 'eBook Link'

    sale_order_id = fields.Many2one('sale.order')
    product_template_id = fields.Many2one('product.template')
    download_link = fields.Char()
    read_link = fields.Char()
