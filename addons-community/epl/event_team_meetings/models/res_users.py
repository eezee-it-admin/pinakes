# -*- coding: utf-8 -*-
import base64
import logging
import requests

from odoo import api, fields, models, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class ResUsers(models.Model):
    _inherit = "res.users"

    @api.model
    def _get_return_url(self):
        return self.env['ir.config_parameter'].sudo().get_param(
            'web.base.url') + "/get_auth_code"

    ms_access_token = fields.Text(
        "Access Token",
        help="The token that must be used to access the Microsoft API.")
    ms_refresh_token = fields.Text('Refresh Token')

    def sanitize_data(self, field_to_sanitize):
        """Sanitize the data to remove white space"""
        return field_to_sanitize.strip()

    def action_refresh_access_token(self):
        '''Get access token from refresh token'''
        ms_refresh_token = self.ms_refresh_token
        if not ms_refresh_token:
            raise UserError(_("Please authenticate to get token."))
        ICP = self.env['ir.config_parameter'].sudo()
        ms_client_id = ICP.get_param('ms_client_id')
        print(ms_client_id)
        ms_client_secret = ICP.get_param('ms_client_secret')
        ms_access_token_url = ICP.get_param('ms_access_token_url')

        ms_refresh_token = self.sanitize_data(ms_refresh_token)
        ms_client_id = self.sanitize_data(ms_client_id)
        ms_client_secret = self.sanitize_data(ms_client_secret)
        ms_access_token_url = self.sanitize_data(ms_access_token_url)

        combine = ms_client_id + ':' + ms_client_secret
        userAndPass = base64.b64encode(combine.encode()).decode("ascii")

        headers = {'Authorization': 'Basic {}'.format(userAndPass)}
        payload = {
            'grant_type': 'refresh_token',
            'refresh_token': ms_refresh_token,
        }
        refresh_token_resp = requests.request(
            "POST", ms_access_token_url, headers=headers, data=payload, timeout=10)

        if refresh_token_resp.status_code == 200:
            try:
                refresh_token = refresh_token_resp.json()
                if 'access_token' in refresh_token:
                    self.write({
                        'ms_access_token': refresh_token.get('access_token'),
                        'ms_refresh_token': refresh_token.get('refresh_token'),
                    })
            except Exception as ex:
                raise UserError(
                    _('Exception during token process: {}').format(ex))
        elif refresh_token_resp.status_code == 401:
            _logger.error(_("Access/Refresh token token has expired."))
        else:
            raise UserError(
                _("Error during process: {}").format(refresh_token_resp.text))

    def action_authenticate(self):
        ICP = self.env['ir.config_parameter'].sudo()
        url = """%s?&response_type=code&scope=user.read offline_access
            mail.read OnlineMeetings.Read OnlineMeetings.ReadWrite
            &response_mode=query&client_id=%s&redirect_uri=%s
            """ % (ICP.get_param('ms_auth_base_url'),
                   ICP.get_param('ms_client_id'),
                   ICP.get_param('ms_request_token_url'))
        return {"type": "ir.actions.act_url", "url": url, "target": "new"}
