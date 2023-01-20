# Copyright 2017-2023 Eezee-IT (<https://www.eezee-it.com>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

import base64
import datetime
import logging
import re
from io import BytesIO
import pandas as pd
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo import api, fields, models

_logger = logging.getLogger(__name__)

EXCEPTION_LOG_TYPE = {
    'danger': "<p style='color:red;'>",
    'warning': "<p style='color:#ffa500;'>",
    'info': "<p>",
    'success': "<p style='color:green;'>",
}


class IrTodoAttachment(models.Model):
    """
    """
    _inherit = 'ir.attachment'

    action_type = fields.Selection([
        ('to_export', 'To Export'),
        ('to_import', 'To Import'),
        ('stay_here', 'No action'),
    ], string='To Do Action', default='stay_here', required=True,
        help="Type of action to do")
    log_queue = fields.Html('Log', copy=False)
    state = fields.Selection([
        ('none', 'None'),
        ('treat', 'To treat'),
        ('progress', 'In progress'),
        ('fail', 'Fail'),
        ('ignored', 'Ignored'),
        ('partial_done', 'Partially done'),
        ('done', 'Done'),
    ], help="State of treatment", default='none')
    exception = fields.Boolean(copy=False)
    sync_file = fields.Boolean("Is synchronization file")

    @api.model
    def clean_old_attachments(self, days=90):
        """
        Function called by a cron to clean old to do attachments.
        @return: True
        """
        last_date = (datetime.datetime.now() + datetime.timedelta(days=-days))
        domain = [
            ('create_date', '<', last_date.strftime(
                DEFAULT_SERVER_DATETIME_FORMAT)),
            ('state', 'not in', ['treat', 'progress']),
            ('sync_file', '=', True),
        ]
        attachments = self.search(domain)
        _logger.info(" %d attachments will be deleted" % (
            len(attachments)
        ))
        attachments.unlink()
        return True

    def toggle_sync_file(self):
        """
        Inverse the value of the field ``sync_file``
        on the records in ``self``.
        """
        for record in self:
            record.sync_file = not record.sync_file

    def action_treat(self, message="Reset", type='info'):
        for rec in self:
            rec.write({'state': 'treat', 'exception': False})
            if message or type:
                rec._log(message=message, type=type)

    def action_progress(self, message="", type="info"):
        for rec in self:
            rec.write({'state': 'progress', 'exception': False})
            if message or type:
                rec._log(message=message, type=type)

    def action_ignore(self, message="", type="info"):
        for rec in self:
            rec.write({'state': 'ignored'})
            if message or type:
                rec._log(message=message, type=type)

    def action_partial_done(self, message="", type="warning"):
        for rec in self:
            rec.write({'state': 'partial_done', 'exception': True})
            if message or type:
                rec._log(message=message, type=type)

    def action_done(self, message="", type="info", exception=False):
        for rec in self:
            rec.write({'state': 'done', 'exception': exception})
            if message or type:
                rec._log(message=message, type=type)

    def action_fail(self, message="", type="danger"):
        for rec in self:
            rec.write({'state': 'fail'})
            if message or type:
                rec._log(message=message, type=type)

    @api.model
    def get_to_treat_files(self, res_model, action_type):
        domain = [('state', '=', 'treat'),
                  ('sync_file', '=', True),
                  ('action_type', '=', action_type),
                  ('res_model', '=', res_model)]
        return self.search(domain)

    @api.model
    def get_all_to_be_exported_files(self):
        domain = [('state', '=', 'treat'),
                  ('sync_file', '=', True),
                  ('action_type', '=', 'to_export')]
        return self.search(domain)

    def _log(self, message="", type=""):
        self.ensure_one()
        if message and not isinstance(message, dict):
            if type and not isinstance(message, dict):
                balise = EXCEPTION_LOG_TYPE[type]
            else:
                balise = u"<p>"
            timing = fields.Datetime.now()
            self.log_queue = "%s%s: %s</p>%s" % (
                balise, str(timing), message, self.log_queue or "")

    def _decode_file(self):
        """
        Encode the file to StringIO
        @:return encode file
        """
        self.ensure_one()
        data = base64.b64decode(self.datas)
        data_file = BytesIO(data)
        return data_file

    def send_to_ftp_server(self, ftps):
        """
        Send all recordset to the ftp server.
        in case of exception the attachment ignored and pass to the next
        @:return True
        """
        for line in ftps:
            for attachment in self:
                if attachment.state not in ('treat', 'fail', 'progress'):
                    continue
                if not attachment.datas:
                    attachment.state = 'ignored'
                    continue
                try:
                    data_file = attachment._decode_file()
                    file_name = re.sub('[^0-9a-zA-Z.]+', '_',
                                       attachment.name)
                    line.upload_file(data_file, file_name)
                    attachment.state = 'done'
                except Exception as e:
                    attachment.update({
                        'state': 'fail',
                        'failure_Reason': '%s' % e,
                        'exception': True
                    })
                    message = """Failed upload file %s -Error: -%s""" % (
                        attachment.name, e)
                    _logger.warning(message)
                    continue
        return

    def process_input_files(self):
        """
        Read and process files.
        You Override This function in your module if you have
        a specific treatment.
        :return:
        """
        for rec in self.filtered(lambda m: m.action_type == 'to_import'):
            if not rec.res_model == 'network.client.line' or not rec.res_id:
                continue
            try:
                config = self.env['network.client.line'].browse(
                    rec.res_id)
                if (config.next_action == 'action_server' and
                        config.ir_actions_server_id):
                    context = {
                        'active_model': self._name,
                        'active_ids': [rec.id],
                        'active_id': rec.id,
                    }
                    action = config.ir_actions_server_id
                    res = action.with_context(context).run()
                    if isinstance(res, dict) and res.get(rec.id, False):
                        if isinstance(res[rec.id], dict):
                            message = res[rec.id]['message']
                            if res[rec.id]['state'] == 'done':
                                rec.action_done(message=message)
                            elif res[rec.id]['state'] == 'fail':
                                rec.action_fail(message=message)
                            elif res[rec.id]['state'] == 'partial_done':
                                rec.action_partial_done(message=message)
            except Exception as e:
                message = 'A error encountered : %s ' % e
                _logger.error(message)
                rec.action_fail(message=message, type="danger")

    def process_output_files(self):
        """
        You Override This function in your module if you have
        a specific treatment.
        :return:
        """
        for r in self.filtered(lambda m: m.action_type == 'to_export'):
            try:
                if not r.res_model == 'network.client.line' or not r.res_id:
                    ftp_config = self.env[
                        'network.client'].get_default_output_server()
                    if not ftp_config:
                        continue
                else:
                    ftp_config = self.env['network.client.line'].browse(
                        r.res_id)
                r.send_to_ftp_server(ftp_config)
            except Exception as e:
                message = 'An error encountered : %s ' % e
                _logger.error(message)
                r.action_fail(message=message, type="danger")
        return

    def process_now(self):
        """Override This function in your module to call the right function
         to use to read this file"""
        in_files = self.filtered(lambda m: m.action_type == 'to_import')
        out_files = self.filtered(lambda m: m.action_type == 'to_export')
        in_files.process_input_files()
        out_files.process_output_files()
        return

    @api.model
    def cron_process_attachments(self):
        to_treat = self.get_to_treat_files(res_model='network.client.line',
                                           action_type='to_import')
        return to_treat.process_now()

    def get_excel_dataframe(self):
        self.ensure_one()
        try:
            data = self._decode_file()
            df = pd.read_excel(data)
            return df
        except Exception as e:
            raise e

    def get_csv_dataframe(self):
        self.ensure_one()
        try:
            data = self._decode_file()
            df = pd.read_csv(data)
            return df
        except Exception as e:
            raise e

    def retry_now(self):
        return True
