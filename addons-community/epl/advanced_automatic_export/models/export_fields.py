# Copyright 2021-2023 Eezee-IT (<http://www.eezee-it.com>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import models, fields, api
from odoo.exceptions import ValidationError
from odoo.tools.safe_eval import safe_eval


class ExternalFields(models.Model):
    _name = "external.fields"
    _description = "Use to make link between Odoo fields and " \
                   "third party software fields"
    _order = "sequence"

    sequence = fields.Integer(default=10)
    name = fields.Char("Label Fields", required=True)
    description = fields.Char()
    config_id = fields.Many2one("automatic.export.config",
                                "External Config", required=True)
    fields_id = fields.Many2one("ir.model.fields", "Field")
    sub_model = fields.Many2one("ir.model")
    relation_fields = fields.Many2one("ir.model.fields", "Sub Field")
    default_value = fields.Char()
    function_name = fields.Char(string='Function',
                                groups='base.group_system')
    technical_field = fields.Char(groups='base.group_system')
    value_format = fields.Selection([
        ('char', 'Char'),
        ('integer', 'Int'),
        ('float', 'Float'),
        ('datetime', 'Date'),
        ('bool', 'Boolean'),
    ], required=True, default='char')
    datetime_format = fields.Char(string="Date Time format")
    max_length = fields.Integer()

    flag_review = fields.Boolean(string='Is ok')
    is_mandatory = fields.Boolean(string='Mandatory')

    _sql_constraints = [
        ('field_name_uniq', 'unique (name,config_id)',
         'Names of fields to be exported must be unique!')
    ]

    @api.constrains('function_name')
    def _check_function_name(self):
        for line in self:
            if (line.function_name and
                    not line.function_name.startswith(('_get', 'get'))):
                msg = "The name of the function must start with _get "
                raise ValidationError(msg)
            # TODO check if the function name is correct

    @api.constrains('technical_field')
    def _check_technical_field(self):
        for line in self:
            if (line.technical_field and
                    line.config_id and line.config_id.model_name):
                try:
                    localdict = {'object': self.env[line.config_id.model_name]}
                    safe_eval(line.technical_field, localdict,
                              mode="exec", nocopy=True)
                except Exception as e:
                    raise ValidationError(e)

    @api.onchange('fields_id')
    def change_fields_id(self):
        if self.fields_id:
            rel = self.fields_id.relation
            if rel:
                model = self.env["ir.model"].search(
                    [('model', '=', rel)], limit=1)
                self.sub_model = model and model.id
                self.relation_fields = False
        else:
            self.sub_model = False
            self.relation_fields = False

    def toggle_status_review(self):
        """ Inverse the value of the field ``flag_review``
        on the records in ``self``.
        """
        for record in self:
            record.flag_review = not record.flag_review
