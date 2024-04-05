# Copyright 2023 Eezee-IT (<http://www.eezee-it.com>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    def _get_all_variants_data(self):
        """This returns all possible combinations of variants for a product"""
        variants = self.product_variant_ids
        variant_data = [{'id': variant.id, 'name': variant.display_name} for variant in variants]
        return {'variants': variant_data}
