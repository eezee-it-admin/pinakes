# -*- coding: utf-8 -*-
import json
import base64
import requests

from odoo import http
from odoo.http import request


class MicrosoftController(http.Controller):

    @http.route('/get_auth_code', type="http")
    def get_auth_code(self, **kwarg):
        "Get access Token and store in current logged-in user"
        msg = ""
        user = request.env.user
        if kwarg.get('code') and user:
            ICP = request.env['ir.config_parameter'].sudo()
            client_id = ICP.get_param('ms_client_id')
            print(client_id)
            client_secret = ICP.get_param('ms_client_secret')
            ms_request_token_url = ICP.get_param('ms_request_token_url')
            combine = client_id + ':' + client_secret
            headers = {'Authorization': 'Basic {}'.format(
                base64.b64encode(combine.encode()).decode("ascii"))}
            payload = {
                'grant_type': 'authorization_code',
                'code': kwarg.get('code'),
                'redirect_uri': ms_request_token_url,
            }
            print(f"Headers: {headers} ; Acess token url: {ms_request_token_url}")
            response = requests.request(
                "POST", ICP.get_param('ms_access_token_url'),
                headers=headers, data=payload, timeout=10)
            if response:
                print('Bingo!')
                token_resp = json.loads(response.text.encode('utf8'))
                user.write({
                    "ms_access_token": token_resp.get('access_token'),
                    "ms_refresh_token": token_resp.get('refresh_token'),
                })
                msg = "Authentication Response: %s." % token_resp
        msg += "<br/><br/><br/>You can Close this window now"
        return msg
