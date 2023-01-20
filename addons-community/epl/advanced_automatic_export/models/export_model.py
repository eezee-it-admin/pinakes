# Copyright 2021      Eezee-IT (<http://www.eezee-it.com>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

import logging
import os
from collections import defaultdict

from odoo import models, fields, api, exceptions, _, registry
from odoo.exceptions import UserError
from odoo.modules.registry import Registry

DEFAULT_DATE_FORMAT = '%Y%m%d'
DEFAULT_TIME_FORMAT = '%H:%M:%S'
_logger = logging.getLogger(__name__)

# mapping separator csv
SEPCSV = {
    'v': ',',
    'pp': ':',
    'sl': '|',
    'pv': ';',
}


class AutomaticExportConfig(models.Model):
    """
    Model to setup communication with external tools
    """
    _name = 'automatic.export.config'
    _description = "Settings to send data externally"

    name = fields.Char(required=True, copy=False)
    note = fields.Text()
    model_id = fields.Many2one("ir.model", "Model", help="Model to export")
    model_name = fields.Char(related='model_id.model', readonly=True, string="Model Name")
    at_create = fields.Boolean("Create", help="Send info during the create")
    at_write = fields.Boolean("Update", help="Send info at each update")
    at_unlink = fields.Boolean("Delete", help="Send info during delete")
    scheduled = fields.Selection([
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('custom', 'Custom'),
    ], default='daily')
    cron_id = fields.Many2one(
        'ir.cron', "Custom Scheduler", ondelete='cascade',
        domain=[('model_id', 'ilike', 'automatic.export'),
                '|', ('active', '=', True), ('active', '=', False)])

    domain = fields.Char(default=[],
                         help="Odoo domain to filter. Only data matching with "
                              "this filter are exported")
    mode_sync = fields.Selection([
        ('all', 'Export All'),
        ('write_date', 'Latest updates'),
        ('create_date', 'Latest creates'),
        ('last_period', 'Since interval periods'),
        ('previous_period', 'Previous periods'),
    ], string="Export only", required=1, default="write_date")
    previous_period = fields.Selection([
        ('last_day', 'Last day'),
        ('last_week', 'Last week'),
        ('last_month', 'Last month'),
        ('last_year', 'Last year'),
    ], string="Last period", default="last_month")
    trg_date_id = fields.Many2one('ir.model.fields', string='Trigger Date',
                                  help="""When should the condition be triggered.
                                      If present, will be checked by the scheduler.
                                      If empty, will be checked at creation and update.""",
                                  domain="[('model_id', '=', model_id), ('ttype', 'in', ('date', 'datetime'))]")
    interval_number = fields.Integer(
        default=1, help="Records that last write or triggered date in this period")
    interval_type = fields.Selection([('hours', 'Hours'),
                                      ('days', 'Days'),
                                      ('weeks', 'Weeks'),
                                      ('months', 'Months')],
                                     string='Interval Unit', default='months')
    url = fields.Char("URL", help="URL to reach the Webservice")
    token = fields.Char(
        copy=False, help="Unique Token used to identify the service")
    use_log = fields.Boolean(help="Save into logs when data are exported")
    service = fields.Selection(
        [('csv', 'CSV'), ('json', 'JSON'), ('excel', 'Excel')],
        required=True, default="csv"
    )
    path = fields.Char(help="Path to file", default="/")
    file_name = fields.Char(help="File name")
    active = fields.Boolean(default=True,
                            help="Enable or disable the export")
    user_id = fields.Many2one("res.users", "User", required=True,
                              default=lambda self: self.env.user.id,
                              help="User used to read data during export")
    use_exception = fields.Boolean("Raise exception",
                                   help="Raise exception (and block "
                                        "create/update/delete) if the "
                                        "export occurs a problem")
    link_fields_ids = fields.One2many("external.fields",
                                      "config_id",
                                      "Linked Fields",
                                      copy=True,
                                      help="Usefull if you want a specific "
                                           "header for a field")
    encode = fields.Char(default="utf-8", help="Select the encodage"
                                               " for the file generated")
    m2m_separator = fields.Char("Separator Many2Many",
                                help="value from many2many will be separated"
                                     " with this element",
                                default="/")
    o2m_separator = fields.Char("Separator One2Many",
                                help="value from one2many will be separated"
                                     " with this element",
                                default="/")
    decimal_sep = fields.Char(string='Decimal Separator', required=True,
                              default='.')
    csv_sep = fields.Selection(
        [('v', ','), ('pv', ';'), ('pp', ':'), ('sl', '|')],
        string='Csv Separator', default='pv', required=True)
    date_format = fields.Char(required=True,
                              default=DEFAULT_DATE_FORMAT)
    time_format = fields.Char(required=True,
                              default=DEFAULT_TIME_FORMAT)
    sequence = fields.Integer(
        help='Used to order configs', default=10)
    export_os = fields.Boolean("Place file on this server")
    export_ftp = fields.Boolean("FTP/SFTP")
    ftp_id = fields.Many2one('network.client.line', "FTP Settings")
    export_email = fields.Boolean("Send by email")
    mail_template_id = fields.Many2one('mail.template', "Mail Template")
    send_immediately = fields.Boolean(default=True)
    mark_as_send = fields.Boolean(default=True)
    last_sync_date = fields.Datetime(
        default=lambda self: fields.Datetime.now(), required=True, copy=False)
    state = fields.Selection([
        ('draft', 'Pending'),
        ('done', 'Confirmed')], index=True, default='draft', copy=False)
    attachment_count = fields.Integer(compute='_compute_attachment_ids')

    _sql_constraints = [
        ('constraint_name', 'unique(name)', _('This name already exist')),
        ('constraint_token', 'unique(token)', _('This token already exist')),
    ]

    def _compute_attachment_ids(self):
        for rec in self:
            attachments = self.env['ir.attachment'].search([
                ('res_id', '=', self.id),
                ('res_model', '=', 'automatic.export.config')
            ])
            rec.attachment_count = len(attachments)

    @api.onchange('export_email')
    def _set_default_mail_template_id(self):
        if self.export_email:
            self.mail_template_id = self.env.ref(
                'advanced_automatic_export.'
                'template_automatic_export_notification',
                False)

    @api.returns('self', lambda value: value.id)
    def copy(self, default=None):
        self.ensure_one()
        default = dict(default or {}, name=_("%s (Copy)") % self.name)
        return super(AutomaticExportConfig, self).copy(default=default)

    def action_reset(self):
        """
        Reset it, and update informations.
        Unlink the related Cron.
        :return:
        """
        self.state = 'draft'

    def action_done(self):
        """
        Generate the related cron and lock it
        :return:
        """
        self.state = 'done'

    def _register_hook(self):
        """ Patch models that should trigger rules based on creation,
            modification, deletion of records.
        """

        # Note: the patched methods must be defined inside another function,
        # otherwise their closure may be wrong. For instance, the function
        # create refers to the outer variable 'create', which you expect to be
        # bound to create itself. But that expectation is wrong if create is
        # defined inside a loop; in that case, the variable 'create' is bound
        # to the last function defined by the loop.

        def make_create():
            """ Instanciate a create method that processes rules. """

            @api.model_create_multi
            def create(self, vals_list, **kw):
                # call original method
                records = create.origin(self, vals_list, **kw)
                export_obj = self.env["automatic.export"]
                export_obj.send_data(records._name, records.ids, "create")
                return records.with_env(self.env)

            return create

        def make_write():
            def write(self, vals, **kw):
                # call original method
                write.origin(self, vals, **kw)
                export_obj = self.env["automatic.export"]
                export_obj.send_data(self._name, self.ids, "write")
                return True

            return write

        def make_unlink():
            def unlink(self, **kwargs):
                export_obj = self.env["automatic.export"]
                export_obj.send_data(self._name, self.ids, "unlink")
                return unlink.origin(self, **kwargs)

            return unlink

        patched_models = defaultdict(set)

        def patch(model, name, method):
            """ Patch method `name` on `model`, unless it has been
            patched already. """
            if model not in patched_models[name]:
                patched_models[name].add(model)
                model._patch_method(name, method)

        # retrieve all actions, and patch their corresponding model
        for rule in self.with_context({}).search([]):
            model = self.env.get(rule.model_id.model)
            # Do not crash if the model was uninstalled
            if model is None:
                _logger.warning("Action rule with ID %d depends on model %s" %
                                (rule.id,
                                 rule.model_name))
                continue

            if rule.at_create:
                patch(model, 'create', make_create())

            if rule.at_write:
                patch(model, 'write', make_write())

            if rule.at_unlink:
                patch(model, 'unlink', make_unlink())

    def _update_registry(self):
        """ Update the registry after a modification on action rules. """
        if self.env.registry.ready and not self.env.context.get('import_file'):
            # for the sake of simplicity, simply force the registry to reload
            self._cr.commit()  # pylint: disable=E8102
            self.env.reset()
            registry = Registry.new(self._cr.dbname)
            registry.registry_invalidated = True

    @api.model
    def create(self, vals):
        res = super(AutomaticExportConfig, self).create(vals)
        self._update_registry()
        return res

    def write(self, vals):
        res = super(AutomaticExportConfig, self).write(vals)
        self._update_registry()
        return res

    def unlink(self):
        res = super(AutomaticExportConfig, self).unlink()
        self._update_registry()
        return res

    def get_fields_list(self):
        """
        Get technical name of fields to send
        :return: list of str
        """
        res = []
        self.ensure_one()
        for line in self.link_fields_ids:
            label = line.name
            field_name = line.fields_id and line.fields_id.name
            res.append((label, field_name))
        return res

    def _get_separator_csv(self):
        """
        Get the csv separator caracter
        :return: caracter
        """
        self.ensure_one()
        if self.csv_sep:
            return SEPCSV[self.csv_sep]
        return ';'

    def load_model(self):
        """
        Load the recordset target and use sudo with the user_id
        :return: target recordset
        """
        self.ensure_one()
        return self.env[self.model_id.model].with_user(self.user_id.id)

    def manage_result(self, result, message):
        """
        Depending on the config, can raise an exception if the result if False
        :param result: boolean
        :param message: str
        :return: bool
        """
        self.ensure_one()
        if self.use_exception and not result:
            message = _("The system occurs a problem during the Web "
                        "Service export.\nPlease contact your "
                        "administrator.\nError message: %s") % message
            raise exceptions.ValidationError(message)
        return True

    def logger(self, message, action_name="sync", level="info"):
        """
        Copy/paste from Odoo (into server action) to create a log and save it
        @param message: str
        @param level: str
        @return: bool
        """
        self.ensure_one()
        if not self.use_log:
            return True
        query = """
        INSERT INTO ir_logging
        (create_date, create_uid, type, dbname, name, level, message,
        path, line, func)
        VALUES (NOW() at time zone 'UTC', %s, %s, %s, %s, %s, %s, %s,
        %s, %s)
        """
        # Ask new cursor to commit
        with registry(self._cr.dbname).cursor() as cr:
            val = (self.env.uid, 'server', cr.dbname, __name__, level, message,
                   "Automatic Export", self.id, action_name)
            cr.execute(query, val)
            cr.commit()  # pylint: disable=E8102

        return True

    @api.onchange('at_create', 'at_write', 'at_unlink')
    def _onchange_action(self):
        res = self.check_alredy_file()
        if res:
            raise UserError(_('File already exist !\n '
                              'Delete it before changing the configuration'))

        if self.at_create or self.at_write:
            self.at_unlink = False
        elif self.at_unlink:
            self.at_create = False
            self.at_write = False

    @api.model
    def check_alredy_file(self):
        if self.service == "csv":
            path = self.path or '/'
            filename = self.file_name
            full_path = path + (filename or '')
            exists = os.path.isfile(full_path)
            if exists:
                return True
        return False

    # If change is done check if a file already exist
    # You can't update if there is already some value
    @api.onchange('link_fields_ids')
    def _onchange_field_ids(self):
        res = self.check_alredy_file()
        if res:
            raise UserError(_('File already exist !\n '
                              'Delete it before changing the configuration'))

    def action_process_now(self):
        self.ensure_one()
        res = self.env['automatic.export'].export_data(self)
        return res

    def action_view_attachments(self):
        self.ensure_one()
        attachments = self.env['ir.attachment'].search([
            ('res_id', '=', self.id),
            ('res_model', '=', 'automatic.export.config')
        ])
        action = {
            'name': 'Generated attachments',
            'views': [
                (self.env.ref('ftp_http_client.view_todo_attachment_tree').id,
                 'tree'),
                (self.env.ref('ftp_http_client.view_todo_attachment_form').id,
                 'form')
            ],
            'res_model': 'ir.attachment',
            'type': 'ir.actions.act_window',
            'target': 'current',
            'domain': [('id', 'in', attachments.ids)]
        }
        return action
