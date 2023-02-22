# Copyright 2021 Eezee-IT (<http://www.eezee-it.com>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).


import json
import logging

import requests
from odoo import _, api, fields, models
from odoo.exceptions import UserError
from werkzeug.urls import url_encode, url_join

_logger = logging.getLogger(__name__)


class MicrosoftOutlookMixin(models.AbstractModel):

    _inherit = 'microsoft.outlook.mixin'

    microsoft_account_id = fields.Many2one('microsoft.account.outlook')

    @api.depends('is_microsoft_outlook_configured')
    def _compute_is_microsoft_outlook_configured(self):
        # pylint: disable=missing-return
        for record in self:
            if record.microsoft_account_id:
                record.is_microsoft_outlook_configured = record.microsoft_account_id.client_id and \
                    record.microsoft_account_id.client_secret
                continue

            super(MicrosoftOutlookMixin, record)._compute_is_microsoft_outlook_configured()

    @api.depends('is_microsoft_outlook_configured')
    def _compute_outlook_uri(self):
        has_microsoft_account = self.filtered('microsoft_account_id')

        if not has_microsoft_account:
            return super(MicrosoftOutlookMixin, self)._compute_outlook_uri()

        base_url = self.get_base_url()
        for record in self:
            if not record.microsoft_account_id:
                super(MicrosoftOutlookMixin, record)._compute_outlook_uri()
                continue

            if not record.id or not record.is_microsoft_outlook_configured:
                record.microsoft_outlook_uri = False
                continue

            record.microsoft_outlook_uri = url_join(
                self._OUTLOOK_ENDPOINT, 'authorize?%s' % url_encode({
                    'client_id': record.microsoft_account_id.client_id,
                    'response_type': 'code',
                    'redirect_uri': url_join(base_url, '/microsoft_outlook/confirm'),
                    'response_mode': 'query',
                    # offline_access is needed to have the refresh_token
                    'scope': 'offline_access %s' % self._OUTLOOK_SCOPE,
                    'state': json.dumps({
                        'model': record._name,
                        'id': record.id,
                        'csrf_token': record._get_outlook_csrf_token(),
                    })
                }))

    def _fetch_outlook_token(self, grant_type, **values):
        self.ensure_one()

        if not self.microsoft_account_id:
            return super(MicrosoftOutlookMixin, self)._fetch_outlook_token(grant_type,
                                                                           **values)

        base_url = self.get_base_url()
        microsoft_outlook_client_id = self.microsoft_account_id.client_id
        microsoft_outlook_client_secret = self.microsoft_account_id.client_secret

        response = requests.post(
            url_join(self._OUTLOOK_ENDPOINT, 'token'),
            data={
                'client_id': microsoft_outlook_client_id,
                'client_secret': microsoft_outlook_client_secret,
                'scope': 'offline_access %s' % self._OUTLOOK_SCOPE,
                'redirect_uri': url_join(base_url, '/microsoft_outlook/confirm'),
                'grant_type': grant_type,
                **values,
            },
            timeout=10,
        )

        if not response.ok:
            try:
                error_description = response.json()['error_description']
            except Exception:
                error_description = _('Unknown error.')
            raise UserError(_('An error occurred when fetching the access token. %s') %
                            error_description)

        return response.json()
