# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class ResUsers(models.Model):
    _inherit = "res.users"

    journal_ids = fields.Many2many('account.journal', 'journal_user_rel',
                                   string='Allowed Journals')

    @api.model_create_multi
    def create(self, vals):
        res = super(ResUsers, self).create(vals)
        self.clear_caches()
        return res

    def write(self, vals):
        res = super(ResUsers, self).write(vals)
        self.clear_caches()
        return res
