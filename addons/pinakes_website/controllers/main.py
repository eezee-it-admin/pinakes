from odoo import http


class WebsiteSale(http.Controller):

    @http.route(['/shop/tag/<model("product.tag"):tag>'], type='http', auth="public", website=True)
    def shop_tag(self, tag, **post):
        domain = [('category_tags_ids', 'in', tag.id)]
        products = request.env['product.template'].search(domain)
        return request.render("website_sale.product_tags", {'products': products})
