# Copyright 2021-2023 Eezee-IT (<http://www.eezee-it.com>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

import base64
import logging
import pandas as pd
from io import BytesIO
from datetime import datetime

from odoo import models

_MAIL_TEMPLATE_FIELDS = ['subject', 'body_html', 'email_from', 'email_to',
                         'email_cc', 'reply_to', 'scheduled_date',
                         'attachment_ids']

_logger = logging.getLogger(__name__)


class IrTodoAttachment(models.Model):
    _inherit = 'ir.attachment'

    def send_files_by_email(self, mail_template):
        mail_mail = self.env['mail.mail']
        for attachment in self:
            try:
                values = mail_template.generate_email(attachment.res_id, _MAIL_TEMPLATE_FIELDS)
                msg = mail_mail.create(values)
                msg.write({'attachment_ids': [(6, 0, attachment.ids)],
                           'subject': attachment.name})
                msg.send()
                attachment.action_done(message="File send by mail")
            except Exception as e:
                message = "Failed to send file %s / %s " % (attachment.name, e)
                attachment.action_fail(message=message, type="danger")
                _logger.error(message)
                continue

    def process_output_files(self, ftp_config=None):
        """
        You Override This function in your module if you have
        a specific treatment.
        :return:
        """
        for r in self.filtered(lambda m: m.action_type == 'to_export'):
            try:
                exportconfig = None
                if r.res_model == 'automatic.export.config' and r.res_id:
                    exportconfig = self.env[r.res_model].browse(r.res_id)
                if exportconfig:
                    if (exportconfig.export_email and
                            exportconfig.mail_template_id):
                        r.send_files_by_email(exportconfig.mail_template_id)
                    if exportconfig.export_ftp and exportconfig.ftp_id:
                        r.send_to_ftp_server(exportconfig.ftp_id)
                    # TODO add option make a copy in the OS path
                else:
                    ftp_config = r.get_default_ftp_server(
                        ftp_config=ftp_config)
                    r.send_to_ftp_server(ftp_config)
            except Exception as e:
                message = 'An error encountered : %s ' % e
                _logger.error(message)
                r.action_fail(message=message, type="danger")

    def export_data_to_csv(
        self, datas, model_name='', file_name='export', res_id=None,
        sep=',', strict_fn=False):
        try:
            df = pd.DataFrame(datas)
            if datas and isinstance(datas, list):
                line_data = datas[0]
                df_order_column = line_data.keys()
                df = df.reindex(columns=df_order_column)
            if strict_fn:
                output_csv_name = file_name
            else:
                output_csv_name = r"%s_%s.csv" % (file_name, datetime.now())
            output_csv_name = output_csv_name.replace(":", "_")
            file_csv_string = df.to_csv(sep=sep, index=False, header=True)
            content = file_csv_string.encode('utf-8')
            return self.create({
                'name': output_csv_name,
                'res_model': model_name,
                'res_id': res_id,
                'datas': base64.b64encode(content),
                'action_type': 'to_export',
                'state': 'treat',
                'sync_file': True
            })
        except Exception as e:
            _logger.error(e)
            raise e

    def auto_fit_xls_column(self, df, writer, sheet_name):
        worksheet = writer.sheets[sheet_name]
        for column in df.columns:
            column_width = max(df[column].astype(str).map(len).max(), len(column))
            col_idx = df.columns.get_loc(column)
            worksheet.set_column(col_idx, col_idx, column_width)

    def auto_format_table(self, df, writer, sheet_name):
        workbook = writer.book
        num_format = "#.##"
        workbook.add_format({"num_format": num_format})
        worksheet = writer.sheets[sheet_name]
        (max_row, max_col) = df.shape
        column_settings = [{'header': column} for column in df.columns]
        worksheet.add_table(0, 0, max_row, max_col - 1, {
            'columns': column_settings,
            'style': 'Table Style Light 11'})
        worksheet.set_column(0, max_col - 1, 12)
        self.auto_fit_xls_column(df, writer, sheet_name)

    def export_data_to_excel(
        self, datas, model_name='', file_name='export', res_id=None,
        sep=',', strict_fn=False):
        try:
            buffer = BytesIO()
            df = pd.DataFrame(datas)
            if strict_fn:
                output_file_name = "%s.xlsx" % file_name
            else:
                output_file_name = "%s_%s.xlsx" % (file_name, datetime.now())
            output_file_name = output_file_name.replace(":", "_")
            with pd.ExcelWriter(buffer) as writer:
                sheet_name = 'Sheet1'
                df.to_excel(writer, index=False)
                self.auto_format_table(df, writer, sheet_name)
                writer.save()
                file_data = base64.b64encode(buffer.getbuffer())
                buffer.close()
                return self.create({
                    'name': output_file_name,
                    'res_model': model_name,
                    'res_id': res_id,
                    'datas': file_data,
                    'action_type': 'to_export',
                    'state': 'treat',
                    'sync_file': True
                })
        except Exception as e:
            _logger.error(e)
            raise e
