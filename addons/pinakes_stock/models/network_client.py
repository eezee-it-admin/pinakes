# -*- coding: utf-8 -*-
# #############################################################################
#
#    Copyright Eezee-It (C) 2017-2020
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
import ftplib
import logging
from sys import platform
import pysftp
from odoo.exceptions import Warning, ValidationError
from odoo import api, fields, models, _

_logger = logging.getLogger(__name__)

MIN_TIMEOUT = 1
MAX_TIMEOUT = 9999


class NetworkClient(models.Model):
    _name = 'network.client'
    _description = "Network Client"

    client_type = fields.Selection(
        [('ftp', 'FTP'), ('sftp', 'SFTP'), ('http', 'HTTP')], required=True,
        default='ftp',
        readonly=True,
        states={'draft': [('readonly', False)]}
    )
    name = fields.Char(required=True, readonly=True,
                       states={'draft': [('readonly', False)]})
    host = fields.Char(required=True, readonly=True,
                       states={'draft': [('readonly', False)]})
    # FTP Client
    port = fields.Integer(required=True, default=21, readonly=True,
                          states={'draft': [('readonly', False)]})
    timeout = fields.Integer(
        required=True, default=15,
        readonly=True,
        states={'draft': [('readonly', False)]},
        help='Timeout value to use for FTP server '
             'connection. Use a value between 1 and 9999')
    login = fields.Char(readonly=True, states={'draft': [('readonly', False)]})
    password = fields.Char(readonly=True,
                           states={'draft': [('readonly', False)]})
    tls = fields.Boolean(readonly=True,
                         states={'draft': [('readonly', False)]})
    line_ids = fields.One2many(
        'network.client.line',
        'client_id',
        'Client Lines',
        readonly=True,
        states={'draft': [('readonly', False)]}
    )
    # For HTTP Client
    request_type = fields.Selection(
        [('get', 'GET'), ('post', 'POST')], default='get',
        readonly=True,
        states={'draft': [('readonly', False)]}
    )
    active = fields.Boolean(default=True)
    scheduled_cron_id = fields.Many2one('ir.cron',
                                        readonly=True,
                                        states={'draft': [('readonly', False)]}
                                        )
    state = fields.Selection([
        ('draft', 'Draft'),
        ('done', 'Done'),
    ], index=True, default='draft',
        copy=False)

    @api.constrains('timeout')
    def _check_timeout(self):
        """
        Check if the timeout is correct
        :return:
        """
        if self.filtered(
                lambda c: c.timeout < MIN_TIMEOUT or c.timeout > MAX_TIMEOUT):
            raise ValidationError(
                _("Invalid timeout value. Insert a value between %s and %s")
                % (MIN_TIMEOUT, MAX_TIMEOUT))

    def connect_ftp(self):
        """
        Connect to the ftp server.
        :return:
        """
        self.ensure_one()
        try:
            if self.client_type == 'ftp':
                if self.tls:
                    ftp_conn = ftplib.FTP_TLS(timeout=self.timeout)
                else:
                    ftp_conn = ftplib.FTP(timeout=self.timeout)
                ftp_conn.connect(host=self.host, port=self.port)
                ftp_conn.login(user=self.login, passwd=self.password)
                if self.tls:
                    ftp_conn.prot_p()
            else:
                if 'win' not in platform:
                    cnopts = pysftp.CnOpts()
                    cnopts.hostkeys = None
                    ftp_conn = pysftp.Connection(host=self.host,
                                                 port=self.port,
                                                 username=self.login,
                                                 password=self.password,
                                                 cnopts=cnopts)
                else:
                    raise ValidationError(_(u'%s /operating system '
                                            u'not supported') % platform)
        except Exception as e:
            raise Warning(
                _(u'SFTP/FTP Error. Could not connect to SFTP/FTP'
                  u' Server\n\n%s') % e)
        return ftp_conn

    def sync(self):
        """
        Download files
        :return:
        """
        self.ensure_one()
        if self.line_ids:
            lines = self.line_ids.filtered(
                lambda r: r.action_type in ['download_upload', 'download'])
            for line in lines:
                try:
                    line.download_files()
                except Exception as e:
                    _logger.info('Exception: %s' % e)
                    pass
            to_export = self.env[
                'ir.attachment'].get_all_to_be_exported_files()
            to_export.process_output_files()
        return True

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
        for rec in self:
            rec.create_related_cron()
            rec.state = 'done'

    def write(self, vals):
        """
        Desactivate/Activate the related cron.
        :param vals:
        :return:
        """
        res = super(NetworkClient, self).write(vals)
        if 'active' in vals:
            for rec in self.filtered(lambda x: x.scheduled_cron_id):
                rec.scheduled_cron_id.active = vals['active']
        return res

    def action_attachments(self):
        """
        Action to go to all attachments related to any network client
        """
        self.ensure_one()
        context = self.env.context
        domain = []
        if context.get('all_attachments'):
            domain.extend([
                '|',
                '&',
                ('res_model', '=', 'network.client'),
                ('res_id', '=', self.id),
                '&',
                ('res_model', '=', 'network.client.line'),
                ('res_id', 'in', self.line_ids.ids),
            ])
        elif context.get('line_attachments'):
            domain.extend([
                ('res_model', '=', 'network.client.line'),
                ('res_id', 'in', self.line_ids.ids),
            ])
        action = self.env.ref("base.action_attachment").read()[0]
        attachment_ids = self.env['ir.attachment'].search(domain).ids
        action.update({
            'domain': [('id', 'in', attachment_ids)],
        })
        return action

    def create_related_cron(self):
        """
        Create a new cron related to this ftp connector
        :param res: self recordset
        :param values: dict
        :return: ir.cron recordset
        """
        self.ensure_one()
        model = self.env.ref(
            "ftp_http_client.model_network_client")
        model_id = model and model.id
        msg = "invalid model ref! Please contact your administrator system"
        if not model_id:
            raise ValidationError(msg)
        vals = {
            'name': '%s_sync_%s' % (self.client_type, self.name),
            'interval_number': 1,
            'interval_type': 'days',
            'numbercall': -1,
            'doall': False,
            'active': False,
            'model_id': model_id,
            'state': 'code',
            'code': 'model.browse(%s).sync()' % self.id,
        }
        if self.scheduled_cron_id:
            self.scheduled_cron_id.update(vals)
        else:
            scheduled_cron = self.env['ir.cron'].sudo().create(vals)
            self.scheduled_cron_id = scheduled_cron and scheduled_cron.id

    def process_now(self):
        """Override This function in your module to call the right function
         to use to read this file"""
        return

    @api.model
    def get_default_output_server(self):
        """
        @return: self
        """
        available_servers = self.search(
            [('state', '=', 'done'), ('client_type', 'in', ['ftp', 'sftp'])])
        for server in available_servers:
            lines = server.line_ids.filtered(
                lambda l: l.action_type in ('download_upload', 'upload'))
            if lines:
                return lines[0]
            else:
                continue
        return False

    @api.model
    def get_default_input_server(self):
        """
        @return: self
        """
        available_servers = self.search(
            [('state', '=', 'done'), ('client_type', 'in', ['ftp', 'sftp'])])
        for server in available_servers:
            lines = server.line_ids.filtered(
                lambda l: l.action_type in ('download_upload', 'download'))
            if lines:
                return lines[0]
            else:
                continue
        return False
