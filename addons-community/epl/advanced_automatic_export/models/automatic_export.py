# Copyright 2021-2023 Eezee-IT (<http://www.eezee-it.com>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

import json
import logging
import os
import re
from collections import OrderedDict
from datetime import datetime, timedelta

import requests
from dateutil.relativedelta import relativedelta
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from odoo.tools.safe_eval import safe_eval
from dateutil.relativedelta import relativedelta
import calendar
from odoo import fields, models, api, exceptions, _

_logger = logging.getLogger(__name__)
"""
    Model to send data using json.
    To use this, you need to inherit this model into the target model
    Example of json sent:
    {
        'token': '3456789',
        'action': "write",
        'ids': [1, 2],
        'model': 'product.template',
        'values':
        [
            {
                'id': 1,
                'name': 'titi',
                'price': 123,
                'target_id': [1],
                'line_ids': [1, 2, 3],
            },
            {
                'id': 2,
                'name': 'toto',
                'price': 55,
                'target_id': [],
                'line_ids': [],
            },
        ],
    }
    """

_intervalTypes = {
    'days': lambda interval: relativedelta(days=interval),
    'hours': lambda interval: relativedelta(hours=interval),
    'weeks': lambda interval: relativedelta(days=7 * interval),
    'months': lambda interval: relativedelta(months=interval),
}


class AutomaticExport(models.AbstractModel):
    _name = 'automatic.export'
    _description = "Automatic export data"

    @api.model
    def get_field_type(self, config, field):
        fields_obj = self.env["ir.model.fields"]
        val = [('name', '=', field), ('model_id', '=', config.model_id.id)]
        res = fields_obj.search(val, limit=1)
        return res.ttype

    @api.model
    def get_relation_field(self, field_line, value, type):
        if field_line.relation_fields:
            sub_field_name = field_line.relation_fields.name
            res = []
            if type == "many2one":
                res_value = getattr(value, sub_field_name, value)
                if isinstance(res_value, models.BaseModel):
                    return getattr(res_value, 'name', res_value)
                return res_value
            else:
                for v in value:
                    value_e = getattr(v, field_line.relation_fields.name,
                                      value)
                    res.append(value_e)
                return res

        return getattr(value, "ids", value)

    @api.model
    def get_o2m_m2m_format(self, type, value, config):
        if type == 'one2many':
            separator = config.o2m_separator
        else:
            separator = config.o2m_separator

        value = str(separator).join([str(v) for v in value])
        return value

    @api.model
    def get_value(self, type, value, field_name, config):
        return value

    @api.model
    def format_value(self, value, out_type, initial_dt_format=None,
                     dt_format=None, max_length=0, rounding=2):
        try:
            if isinstance(value, bool) and not value and out_type != 'bool':
                return ''
            value = re.sub("[\\!@#$%^&()[]{},;<>?|`~]", " ", str(value))
            if not value:
                return value
            if out_type == 'int':
                value = int(value)
            elif out_type == 'float':
                value = float(value)
                value = round(value, rounding)
            elif out_type == 'datetime':
                # Try to convert string date to a date time check with
                # more than one format
                for dtf in [initial_dt_format,
                            DEFAULT_SERVER_DATETIME_FORMAT,
                            DEFAULT_SERVER_DATE_FORMAT]:
                    try:
                        value = str(value).split('.')[0]
                        date_value = datetime.strptime(value, dtf)
                        value = date_value.strftime(dt_format)
                        break
                    except Exception as er:
                        _logger.error(er)
                        continue
            elif out_type == 'bool':
                value = bool(value)
            else:
                value = str(value)
                if max_length > 0:
                    value = value[:max_length]
        except Exception as e:
            _logger.error(e)
            pass

        return value

    def load_fields_values(self, config, record):
        """
        From the current recordset, load value from current field
        :param config: automatic.export.config recordset
        :return: dict
        """
        record.ensure_one()
        record_sudo = record.sudo()
        values = OrderedDict()
        for line in sorted(config.link_fields_ids, key=lambda a: a.sequence):
            default_dt_format = DEFAULT_SERVER_DATETIME_FORMAT
            label = line.name
            value = ''
            max_length = line.max_length
            if line.fields_id:
                field_name = line.fields_id.name
                value = getattr(record_sudo, field_name, '')
                if line.fields_id.ttype == 'date':
                    default_dt_format = DEFAULT_SERVER_DATE_FORMAT
                # type = line.get_field_type(config, field_name)
                type = line.fields_id.ttype
                if (value and type in ('one2many', 'many2many') and
                        max_length):
                    value = value[:line.max_length]
                    # after filter Reset the max length for one2many/many2many
                    max_length = 0
                value = self.get_relation_field(line, value, type)
                if type in ('one2many', 'many2many'):
                    value = self.get_o2m_m2m_format(type, value, config)
                value = self.get_value(type, value, field_name, config)
            if not value and line.default_value:
                value = line.default_value

            if not value and line.function_name:
                # You can create a custom function to get a complex value
                try:
                    get_func_name = line.function_name
                    get_func = getattr(record_sudo, get_func_name, None)
                    value = get_func()
                except Exception as e:
                    _logger.error(e)
                    value = ''
            if not value and line.technical_field:
                # You can create a custom function to get a complex value
                try:
                    localdict = {'object': record}
                    value = safe_eval(line.technical_field, localdict)
                except Exception as e:
                    _logger.error(e)
                    value = ''
            dt_format = (line.datetime_format or line.config_id.date_format or
                         DEFAULT_SERVER_DATE_FORMAT)
            formatted_value = self.format_value(
                value, line.value_format, initial_dt_format=default_dt_format,
                dt_format=dt_format,
                max_length=max_length)
            values.update({
                label: formatted_value,
            })
        return values

    def load_config(self, model, action=""):
        """
        Load configuration depending on the current model and action.
        It could have more than one configuration
        :param action: str
        :param model: str
        :return: automatic.export.config recordset
        """
        domain = False
        config_obj = self.env['automatic.export.config']
        if action == "create":
            domain = [('at_create', '=', True)]
        elif action == "write":
            domain = [('at_write', '=', True)]
        elif action == "unlink":
            domain = [('at_unlink', '=', True)]
        if not domain:
            return config_obj
        domain += [
            ('model_id.model', '=', model),
            ('active', '=', True),
        ]
        configs = config_obj.sudo().search(domain)
        return configs

    def prepare_data(self, config, action, records):
        """
        Prepare data to send it after
        :param config: send.data.config recordset
        :param action: str
        :return: dict
        """
        values = []
        # During delete, we don't care to have values
        if action != "unlink":
            for record in records:
                values.append(self.load_fields_values(config, record))

        data = {
            'values': values,
            'action': action,
            'ids': records.ids,
            'model': records._name,
        }
        return data

    def prepare_data_json(self, config, action, records):
        """
        Specific data for json
        :param config: send.data.config recordset
        :param action: str
        :return: dict
        """
        data = self.prepare_data(config, action, records)
        data['token'] = config.token
        return data

    def prepare_data_csv(self, config, action, records):
        """
        Specific data for csv
        :param config: send.data.config recordset
        :param action: str
        :return: dict
        """
        return self.prepare_data(config, action, records)

    @api.model
    def evaluate_domain(self, config):
        """
        Evaluate the domain and get matching records
        :param config: send.data.config recordset
        :return: target recordset
        """
        domain = []
        if config.domain:
            domain = config.domain
            ctx = self.env['ir.actions.actions']._get_eval_context()
            domain = safe_eval(domain, ctx)
        today = fields.Date.today()
        date_format = "%Y-%m-%d"
        records = config.load_model().search(domain)
        if (config.mode_sync in ('write_date', 'create_date') and
                config.last_sync_date):
            records = records.filtered(
                lambda r: getattr(r,
                                  config.mode_sync) >= config.last_sync_date)
        elif config.mode_sync == 'last_period':
            interval_type = config.interval_type or 'months'
            interval_number = config.interval_number or 1
            from_date = fields.Datetime.now() - _intervalTypes[interval_type](
                interval_number)
            if config.trg_date_id:
                records = records.filtered(
                    lambda r: r[config.trg_date_id.name] and
                              r[config.trg_date_id.name] >= from_date)
            else:
                records = records.filtered(
                    lambda r: r.write_date and r.write_date >= from_date)
        elif config.mode_sync == 'previous_period':
            if config.previous_period == 'last_year':
                prev_date = today - relativedelta(years=1)
                start_period = prev_date.strftime("%Y-01-01")
                end_period = (prev_date.strftime("%Y-12-") +
                              str(calendar.monthrange(today.year, 12)[1]))
            elif config.previous_period == 'last_month':
                prev_date = today - relativedelta(months=1)
                start_period = prev_date.strftime("%Y-%m") + '-01'
                end_period = prev_date.strftime("%Y-%m-") + \
                             str(calendar.monthrange(prev_date.year, prev_date.month)[1])
            elif config.previous_period == 'last_week':
                prev_date = today - relativedelta(weeks=1)
                dates = [prev_date + timedelta(days=i) for i in
                         [0 - prev_date.weekday(), 6 - prev_date.weekday()]]

                start_period = dates[0].strftime(date_format)
                end_period = dates[1].strftime(date_format)
            else:
                prev_date = today - relativedelta(days=1)
                start_period = prev_date.strftime(date_format)
                end_period = prev_date.strftime(date_format)

            if config.trg_date_id:
                records = records.filtered(
                    lambda r: (r[config.trg_date_id.name] and
                               start_period <= r[config.trg_date_id.name].strftime(date_format) <= end_period))
            else:
                records = records.filtered(
                    lambda r: r.write_date and start_period <= r.write_date.strftime(date_format) <= end_period)

        return records

    def send_data(self, model, id_to_treat, action):
        """
        Evaluate the domain
        :param action: str
        :return: bool
        """
        configs = self.load_config(model, action)
        for config in configs.filtered(lambda c: c.active):
            message = False
            result = True
            try:
                results = self.evaluate_domain(config)
                cur_brw = self.env[model].browse(id_to_treat)
                match = cur_brw.filtered(lambda s: s in results)
                if match:
                    if config.service == 'json':
                        values = self.prepare_data_json(config, action, match)
                        result, message = self.contact_url(config, values)
                    elif config.service == 'csv':
                        values = self.prepare_data_csv(config, action, match)
                        result, message = self.write_csv(config, values)
            except Exception as e:
                result = False
                message = str(e)
                _logger.error(e)
            config.manage_result(result, message)

    @api.model
    def _check_directories_access(self, directory, create_if_not_exist=True):
        _logger.debug("Check directory: %s", directory)
        if create_if_not_exist and not os.path.isdir(directory):
            try:
                os.mkdir(directory, 0o775)
            except OSError:
                _logger.error(
                    "Creation of the directory %s failed" % directory)
                return False

        if not os.path.isdir(directory):
            _logger.error(
                "Directory doesn't exist or wrong rights: %s",
                directory)

            return False

        if not os.access(directory, os.W_OK):
            _logger.error(
                "Directory is not writable: %s",
                directory)
            return False

        return True

    @api.model
    def check_linked_fields(self, d, config):
        res = d
        link_obj = self.env["external.fields"]
        val = [('config_id', '=', config.id),
               ('fields_id.name', '=', d)]
        link_ids = link_obj.search(val, limit=1)
        for line in link_ids:
            res = line.name or d
        return res

    @api.model
    def encode_file(self, codage, val):
        encoded = val.encode(codage)
        decoded = encoded.decode(codage)
        return decoded

    @api.model
    def _check_file(self, full_path, data, config):
        codage = config.encode or 'utf-8'
        exists = os.path.isfile(full_path)
        if not exists:
            # Add header
            line = ""
            file = open(full_path, "w", encoding=codage)
            for d in data[0]:
                link = self.check_linked_fields(d, config)
                line += str(link) + ";"
                continue

            if not config.scheduled:
                line += "added_date;"

            line += "\n"
            dec = self.encode_file(codage, line)
            file.write(dec)
            file.close()
        return True

    # If there is no value, we receive False
    # If it is not a boolean, we replace False by ''
    @api.model
    def check_boolean(self, field, config):
        ttype = self.get_field_type(config, field)
        if ttype == "boolean":
            return "False"
        return ''

    @api.model
    def remove_csv(self, config):
        path = config.path
        filename = config.file_name
        if path and filename:
            full_path = path + filename
            if os.path.isfile(full_path):
                os.remove(full_path)

    @api.model
    def write_csv(self, config, values):
        codage = config.encode or 'utf-8'
        last_column = datetime.now()
        last_column = last_column.strftime('%Y-%m-%d %H:%M:%S')
        path = config.path
        filename = config.file_name
        data = values["values"]
        action = values["action"]
        ids = values["ids"]
        message = "Info sent:\nConfig id: %d\nPath: %s\nFilename: %s\n" \
                  "Data: %s\n" % (config.id, path, filename, data)
        level = "info"
        success = True
        error_message = ""
        if path and filename:
            dir_exist = self._check_directories_access(path)
            if dir_exist:
                line = ""
                full_path = path + filename
                self._check_file(full_path, data, config)
                file = open(full_path, "a", encoding=codage)
                if action == "unlink":
                    line += str(ids)
                else:
                    for d in data[0]:
                        if str(data[0][d]) == "False":
                            res_bool = self.check_boolean(d, config)
                            line += res_bool + ";"
                        else:
                            line += str(data[0][d]) + ";"

                if not config.scheduled:
                    line += str(last_column) + ";"

                line += "\n"
                dec = self.encode_file(codage, line)
                file.write(dec)
                file.close()
                message += _("Line add %s \n") % line
            else:
                error_message += _("Error during path check: %s \n") % path
                success = False
                level = "error"

        else:
            error_message += _("No File or path define for "
                               "config: %s \n") % config.name
            success = False
            level = "error"

        message += error_message
        if level != 'info':
            config.logger(message, action_name="sync", level=level)

        return success, error_message

    @api.model
    def contact_url(self, config, values):
        """
        Send data directly to the url from the config
        :param config: send.data.config recordset
        :param values: list of dict
        :return: bool, message
        """
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        url = config.url
        values_json = json.dumps(values)
        message = "Info sent:\nConfig id: %d\nURL: %s\nData: %s" % \
                  (config.id, url, values_json)
        level = "info"
        success = True
        error_message = ""
        try:
            result = requests.post(url, data=values_json, headers=headers)
            message += "\nResult: %s" % result
            if result.status_code != 200:
                error_message = _("Status code: %s") % result.status_code
                raise exceptions.ValidationError(error_message)
        except exceptions.ValidationError as e:
            success = False
            level = "error"
            error_message = e
            message += "\nError: %s" % e
        except Exception as e:
            success = False
            level = "error"
            error_message = e
            message += "\nError: %s" % e
        if level != 'info':
            config.logger(message, action_name="sync", level=level)
        return success, error_message

    @api.model
    def run_export_cron(self, scheduled):
        config_env = self.env['automatic.export.config']
        domain = [
            ('scheduled', '=', scheduled),
            ('active', '=', True),
            ('state', '=', 'done')
        ]

        configs = config_env.search(domain, order='sequence')
        for config in configs:
            try:
                result, message = self.export_data(config)
                config.manage_result(result, message)
            except Exception as e:
                _logger.error(e)
                config.logger(e, action_name="sync", level="error")
                pass

    @api.model
    def export_data(self, config, records=None):
        message = False
        result = True
        irAttachment = self.env['ir.attachment']
        try:
            sync_time = fields.Datetime.now()
            if not records:
                records = self.evaluate_domain(config)
            self.remove_csv(config)
            if config.service == 'json':
                values = self.prepare_data_json(config, '', records)
                result, message = self.contact_url(config, values)
                config.last_sync_date = sync_time
            elif config.service in ('csv', 'excel'):
                values = self.prepare_data_csv(config, '', records)
                file_name = config.file_name or config.name or config._name
                if config.service == 'csv':
                    sep_csv = config._get_separator_csv()
                    attachment = irAttachment.export_data_to_csv(
                        values["values"], model_name=config._name,
                        file_name=file_name, res_id=config.id, sep=sep_csv)
                elif config.service == 'excel':
                    attachment = irAttachment.export_data_to_excel(
                        values["values"], model_name=config._name,
                        file_name=file_name, res_id=config.id,
                        sep=',', strict_fn=False)
                else:
                    attachment = irAttachment.export_data_to_excel(
                        values["values"], model_name=config._name,
                        file_name=file_name, res_id=config.id)
                if not attachment:
                    message = 'there are no file was generated'
                    config.logger(message, action_name="sync", level="error")
                elif config.send_immediately:
                    try:
                        attachment.process_now()
                        config.last_sync_date = sync_time
                        if config.mark_as_send and records:
                            data = {}
                            if hasattr(records[0], 'auto_exported'):
                                data.update(auto_exported=True)
                            if hasattr(records[0], 'auto_sent_time'):
                                data.update(auto_sent_time=sync_time)
                            if data:
                                records.update(data)
                    except Exception as e:
                        message = "Failed sending the file '%s' Error:'%s" % (
                            attachment.name, e)
                        config.logger(message, action_name="sync",
                                      level="error")
                else:
                    config.last_sync_date = sync_time
        except Exception as e:
            result = False
            message = str(e)
            _logger.error(e)
            config.logger(message, action_name="sync", level="error")
        return result, message

    @api.model
    def export(self, config_ids=[]):
        config_env = self.env['automatic.export.config']
        for config_id in config_ids:
            try:
                config = config_env.browse(config_id)
                if (config.scheduled != 'custom' or config.state != 'done' or
                        not config.active):
                    continue
                result, message = self.export_data(config)
                config.manage_result(result, message)
            except Exception as e:
                _logger.error(e)
                config.logger(e, action_name="sync", level="error")
                pass
