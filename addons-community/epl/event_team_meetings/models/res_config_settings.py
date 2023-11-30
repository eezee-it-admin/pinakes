# -*- coding: utf-8 -*-
from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    @api.model
    def _get_return_url(self):
        return self.env['ir.config_parameter'].sudo().get_param(
            'web.base.url') + "/get_auth_code"

    module_event_team_meetings = fields.Boolean("Microsoft Team Meetings")
    ms_client_id = fields.Char(
        "Application ID", config_parameter="ms_client_id")
    ms_client_secret = fields.Char(
        "Client Secret", config_parameter="ms_client_secret")
    ms_auth_base_url = fields.Char(
        "Authorization URL",
        config_parameter="ms_auth_base_url",
        default="https://login.microsoftonline.com/common/oauth2/v2.0"
        "/authorize",
        help="User authenticate URI")
    ms_access_token_url = fields.Char(
        "Authorization Token URL",
        config_parameter="ms_access_token_url",
        default="https://login.microsoftonline.com/common/oauth2/v2.0/token",
        help="Exchange code for refresh and access tokens")
    ms_request_token_url = fields.Char(
        "Redirect URL",
        config_parameter="ms_request_token_url",
        help="One of the redirect URIs listed for this project in "
        "the developer dashboard.",
        default=_get_return_url)

    def action_authenticate(self):
        return self.env.user.action_authenticate()

    def action_refresh_access_token(self):
        return self.env.user.action_refresh_access_token()
