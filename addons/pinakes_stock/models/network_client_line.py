# -*- coding: utf-8 -*-
# #############################################################################
#
#    Copyright Eezee-It (C) 2020
#    Author: Eezee-It <info@eezee-it.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Lesser General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Lesser General Public License for more details.
#
#    You should have received a copy of the GNU Lesser General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################
import base64
import ftplib
import io
import logging
import requests
from odoo.exceptions import Warning
from odoo import api, fields, models, exceptions, _

_logger = logging.getLogger(__name__)


class NetworkClientLine(models.Model):
    _name = 'network.client.line'
    _description = "Network Client line"

    name = fields.Char(required=True)
    upload_path = fields.Char(
        'Upload directory', default='/',
        help='A comma separated list of UNIX paths where files'
             ' will be uploaded. Ex: tmp,uploads/oe')
    type_download_link = fields.Selection([
        ('start_with', 'File Name Start with'),
        ('contains', 'File Name contains'),
        ('has_name', 'File Name Is'),
        ('all', 'All Files in directory'),
    ], 'Type of download link', default='has_name', required=True,
        help="Type of download link: \n if File Name Start with"
             "\n we should put the initial characters with which start"
             " file to download example = partner,clients"
             "\n if File Name contains"
             "\n we should put the words with which start"
             " file to download example = partner,clients"
             "\n if File Name Is"
             "\n we should put the exact name of the file to download")
    download_directory = fields.Char(default='/', help='Ex: /payments/new')
    initial_path = fields.Char(
        'filenames ', help='A comma separated list of words that start with'
                           'or in the file name that will be download its.'
                           'Ex:file')
    delete_downloaded_files = fields.Boolean(
        string="Delete files downloaded from FTP server", default=False
    )
    archive_downloaded_files = fields.Boolean(
        string="Archive files downloaded from FTP server", default=True
    )
    archive_path = fields.Char(
        'Archive directory', default='/', help='Ex: /archive')
    client_id = fields.Many2one(
        'network.client',
        string="Network Client", ondelete='cascade')
    client_type = fields.Selection(related='client_id.client_type')
    parameter_ids = fields.One2many(
        'network.client.parameter',
        'client_line_id',
        'Parameters')
    action_type = fields.Selection([
        ('download_upload', u'Download & Upload'),
        ('download', 'Download only'),
        ('upload', 'Upload only'),
    ], string="Action", default='download_upload', required=True,
        help="The action that will be executed for this line")
    model_id = fields.Many2one('ir.model', 'Target Model',
                               domain=[('transient', '=', False)])
    next_action = fields.Selection(
        [('none', 'Anything'),
         ('action_server', 'Execute an action server')],
        default="none", required=True)
    ir_actions_server_id = fields.Many2one(
        'ir.actions.server', 'Execute This Server action',
        domain=lambda self: [(
            'model_id', '=', self.env['ir.model']._get('ir.attachment').id)],
        ondelete='restrict')

    _sql_constraints = [
        ('name_uniq', 'UNIQUE (name)', _('Line name must be unique!'))
    ]

    @api.constrains('ir_actions_server_id')
    def check_ir_actions_server(self):
        """
        Constrains on the field ir_actions_server_id.
        The ir_actions_server_id should be link to ir.attachment object
        """
        for line in self:
            if (line.ir_actions_server_id and
                    line.ir_actions_server_id.model_id.model !=
                    'ir.attachment'):
                raise Warning(
                    _("the action should be linked to the "
                      "ir.attachment model"))

    @api.model
    def load_from_name(self, name):
        """
        Start FTP/HTTP by given name
        :param name: str
        :return: bool
        """
        result = self.search([('name', '=', name)], limit=1)
        if result:
            result.run_config()
            return True
        return False

    def run_config(self):
        """
        Run the FTP/HTTP
        :return:
        """
        for this in self:
            try:
                if this.client_type in ('ftp', 'sftp'):
                    this.download_files()
                elif this.client_type == 'http':
                    this.download_from_http()
            except Exception as e:
                _logger.error("Error on Run the FTP/HTTP: %s" % e)
                pass

    def _get_file_paths_by_name(self, ftp_conn):
        """
        Returns file paths to download.
        Exclude paths to unexisting files and paths to directories
        """
        self.ensure_one()
        initial_files = []
        if self.initial_path and self.type_download_link != 'all':
            initial_files = [sf for sf in self.initial_path.strip().split(',')]
        paths = []
        main_directory = self.download_directory or '/'
        try:
            ftp_conn.cwd(main_directory)
            if self.client_type == 'ftp':
                all_files = ftp_conn.nlst()
            else:
                all_files = ftp_conn.listdir()
            for file in all_files:
                if self.type_download_link == 'start_with':
                    if file.lower().startswith(tuple(initial_files)):
                        paths.append(main_directory + '/' + file)
                elif self.type_download_link == 'contains':
                    if any(s in file.lower() for s in tuple(initial_files)):
                        paths.append(main_directory + '/' + file)
                elif self.type_download_link == 'all':
                    paths.append(main_directory + '/' + file)
                else:
                    if file.lower() in tuple(initial_files):
                        paths.append(main_directory + '/' + file)
        except ftplib.error_perm as e:
            _logger.error("_get_file_paths_start_with %s" % e)
            pass
        return paths

    def _get_file_paths(self):
        """
        Returns file paths to download.
        Exclude paths to unexisting files and paths to directories
        """
        self.ensure_one()
        ftp_conn = self.client_id.connect_ftp()
        paths = self._get_file_paths_by_name(ftp_conn)
        file_paths = []
        for path in paths:
            try:
                if self.client_type == 'ftp':
                    ftp_conn.sendcmd('MDTM ' + path)
                    file_paths.append(path)
                else:
                    if ftp_conn.isfile(path):
                        file_paths.append(path)
            except ftplib.error_perm as e:
                _logger.error("_get_file_paths: %s" % e)
                pass
        return file_paths

    def attach_file(self, content, filename=False):
        """
        Save the file into attachment
        """
        self.ensure_one()
        attachment_obj = self.env['ir.attachment']
        if not filename:
            today = fields.Datetime.now()
            filename = "%s" % today
        data = base64.b64encode(content)
        attachment = attachment_obj.create({
            'name': filename,
            'res_model': self._name,
            'res_id': self.id,
            'datas': data,
            'action_type': 'to_import',
            'state': 'treat',
            'sync_file': True
        })
        return attachment

    def delete_ftp_files(self, filepaths):  # pragma: no cover
        """
        Delete file from FTP
        @param names: list of str
        @return: bool
        """
        self.ensure_one()
        if not isinstance(filepaths, list):
            filepaths = [filepaths]
        ftp_conn = self.client_id.connect_ftp()
        for path in filepaths:
            try:
                if self.client_type == 'ftp':
                    ftp_conn.delete(path)
                else:
                    ftp_conn.remove(path)
            except ftplib.error_perm as reason:
                _logger.warning(reason)
        if self.client_type == 'ftp':
            ftp_conn.quit()
        else:
            ftp_conn.close()
        return True

    def check_valid_paths(self, paths):
        """
        in the ftp server, check file paths and return only valid paths
        @return: list of paths
        """
        self.ensure_one()
        valid_paths = []
        for path in paths:
            try:
                ftp_conn = self.client_id.connect_ftp()
                if self.client_type == 'ftp':
                    filesize = ftp_conn.size(path)
                    if filesize > 0:
                        valid_paths.append(path)
                    ftp_conn.quit()
                else:
                    if ftp_conn.exists(path):
                        valid_paths.append(path)
                    ftp_conn.close()
            except Exception as e:
                _logger.warning(e)
        return valid_paths

    def archive_ftp_files(self, filepaths, filename):
        """
        Archive file from FTP
        @param filepaths: list of src paths
        @param filename: the file name
        @return: bool
        """
        self.ensure_one()
        if not isinstance(filepaths, list):
            filepaths = [filepaths]
        ftp_conn = self.client_id.connect_ftp()
        dest_dir = (self.archive_path or '/').strip()
        today = fields.Datetime.now()
        dest_path = "%s/%s-%s" % (
            dest_dir, str(today).replace(':', '-'), filename)
        for path in filepaths:
            try:
                _logger.info('Start Archiving %s in %s .... ' %
                             (path, self.archive_path))
                ftp_conn.rename(path, dest_path)
                _logger.info('Archiving %s in %s finished' %
                             (path, self.archive_path))
            except ftplib.error_perm as reason:
                _logger.warning(reason)
                raise Warning(
                    _(u'Archiving file failed.\n%s') % reason)
        if self.client_type == 'ftp':
            ftp_conn.quit()
        else:
            ftp_conn.close()
        return True

    def download_files(self):
        """
        Load files
        @return: dict
        """
        self.ensure_one()
        file_paths = self._get_file_paths()
        _logger.info('Start FTP connection to %s:%s' % (
            self.client_id.host, self.client_id.port))
        ftp_conn = self.client_id.connect_ftp()
        for file_path in file_paths:
            try:
                _logger.info('Downloading file %s' % file_path)
                if self.client_type == 'ftp':
                    content = self.download_from_ftp(ftp_conn, file_path)
                else:
                    content = self.download_from_sftp(ftp_conn, file_path)
                filename = file_path.split('/')[-1]
                self.attach_file(content, filename)
                if self.archive_downloaded_files:
                    self.archive_ftp_files(file_path, filename)
                elif self.delete_downloaded_files:
                    self.delete_ftp_files(file_path)
                _logger.info('Download %s finished' % file_path)
            except Exception as e:
                _logger.error(e)
                continue
        if self.client_type == 'ftp':
            ftp_conn.quit()
        else:
            ftp_conn.close()
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'network.client',
            'target': 'current',
            'res_id': self.client_id.id,
        }

    def download_from_ftp(self, ftp_conn, filepath):
        filepath = filepath.strip()
        data = io.BytesIO()
        try:
            ftp_conn.retrbinary('RETR %s' % filepath, data.write)
        except Exception as e:
            raise Warning(_(u'FTP Error, Could not download file from '
                            u'FTP Server\n\n%s') % e)
        return data.getvalue()

    def download_from_sftp(self, ftp_conn, filepath):
        filepath = filepath.strip()
        data = io.BytesIO()
        try:
            ftp_conn.getfo(filepath, data)
        except Exception as e:
            raise Warning(_(u'SFTP Error, Could not download file from '
                            u'SFTP Server\n\n%s') % e)
        return data.getvalue()

    def download_from_http(self):  # pragma: no cover
        self.ensure_one()
        r = self.get_http_response()
        if r.status_code == 200:
            return self.attach_file(r.content)
        raise Warning(_("Unsuccessful response from server"))

    def action_line_attachments(self):
        """
        Action to go to all attachments related to a line
        """
        action = self.env.ref("base.action_attachment").read()[0]
        attachment_ids = self.env['ir.attachment'].search([
            ('res_model', '=', self._name),
            ('res_id', '=', self.id)
        ]).ids
        action.update({
            'domain': [('id', 'in', attachment_ids)],
        })
        return action

    def get_params(self):
        self.ensure_one()
        parameters = {}
        if self.parameter_ids:
            parameters = {p.name: p.value for p in self.parameter_ids}
        return parameters

    def get_http_response(self):  # pragma: no cover
        try:
            params = self.get_params()
            if self.client_id.request_type == 'get':
                r = requests.get(self.client_id.host, params=params)
            else:
                r = requests.post(self.client_id.host, data=params)
        except Exception as e:
            raise Warning(
                _(u'Connection to HTTP server failed.\n%s') % e.message)
        return r

    def check_http_response(self, response):  # pragma: no cover
        if response.status_code == 200:
            raise Warning(_("Successful connection to host"))
        else:
            raise Warning(_("Failed connection. Error %s. %s") % (
                response.status_code, response.reason))

    def test_http_connection(self):  # pragma: no cover
        r = self.get_http_response()
        self.check_http_response(r)

    def test_ftp_connection(self):  # pragma: no cover
        ftp_conn = self.client_id.connect_ftp()
        try:
            if self.client_type == 'ftp':
                ftp_conn.retrlines('LIST')
            else:
                ftp_conn.listdir()
        except Exception as e:
            raise Warning(_(u'Connection to ftp/sftp server is failed. %s'
                            ) % e)
        else:
            message_title = _(
                "Connection Test Succeeded!\n"
                "Everything seems properly set up for FTP/SFTP Sync!")
            raise Warning(message_title)
        finally:
            if self.client_type == 'ftp':
                ftp_conn.quit()
            else:
                ftp_conn.close()
        return True

    @api.model
    def check_file_exist(self, ftp_conn, filepath):
        """
        Not support sftp cnx yet!
        :param ftp_conn:
        :param filepath:
        :return:
        """
        #  Test to see if the file exists by getting the file size by name.
        #  If a None is returned, the file does not exist
        try:
            fileSize = ftp_conn.size(filepath)
        except Exception:
            fileSize = None
            pass
        if fileSize is None:
            _logger.info("_______file does not exist_________")
            return False
        else:
            _logger.info("file exists and is " +
                         str(fileSize) + " bytes in size")
            return True

    def upload(self, ftp_conn, filedata, filepaths):
        self.ensure_one()
        try:
            for filepath in filepaths:
                file_data = io.StringIO(filedata.encode('utf-8'))
                if self.client_type == 'ftp':
                    ftp_conn.storbinary('STOR %s' % filepath, file_data)
                else:
                    ftp_conn.putfo(file_data, filepath)
        except Exception as e:
            msg = _("FTP Error, Could not upload file to FTP Server\n\n%s") % e
            raise exceptions.Warning(msg)
        return True

    def upload_file(self, file, file_name):
        self.ensure_one()
        try:
            ftp_conn = self.client_id.connect_ftp()
            filepath = "%s/%s" % (self.upload_path, file_name)
            filepath = filepath.replace(":", "-")
            if self.client_type == 'ftp':
                stor = 'STOR %s' % (filepath,)
                ftp_conn.storbinary(stor, file)
            else:
                ftp_conn.putfo(file, filepath)
            file.close()
        except Exception as e:
            msg = _("FTP Error, Could not upload file to FTP Server\n\n%s") % e
            raise exceptions.Warning(msg)
