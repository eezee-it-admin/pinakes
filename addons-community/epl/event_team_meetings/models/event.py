# -*- encoding: utf-8 -*-
import logging
import requests

from odoo import fields, models, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class Event(models.Model):
    _inherit = 'event.event'

    ms_meeting_url = fields.Text('Meeting URL')
    ms_meeting_id = fields.Text('Meeting ID')

    def send_meeting_mail_notification(self):
        "Send MS Team Meeting email to event attendees"
        self.ensure_one()
        template = self.env.ref(
            'event_team_meetings.send_ms_meeting_invitation')
        if not template:
            return True
        for attendee in self.registration_ids.filtered(
                lambda att: att.state in ['open'] and att.partner_id.email):
            template.send_mail(
                attendee.id,
                email_values={'email_to': attendee.partner_id.email}
            )
        return True

    def join_ms_meeting_url(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_url",
            "url": self.ms_meeting_url,
        }

    def action_create_ms_meeting(self):
        "Create MS Team Meetings"
        event_mail_obj = self.env['event.mail']
        template = self.env.ref(
            'event_team_meetings.send_ms_meeting_invitation')
        for event in self:
            user = event.user_id
            if not user:
                raise UserError(_(
                    "Please assign responsible person in event."))
            # Refresh token
            user.action_refresh_access_token()
            start_time = str(event.date_begin).\
                replace(' ', 'T') + '.0000000-00:00'
            end_time = str(event.date_end).replace(' ', 'T') + '.0000000-00:00'
            if user.ms_access_token:
                ms_access_token = user.sanitize_data(
                    user.ms_access_token)
                bearer = 'Bearer ' + ms_access_token
                headers = {
                    "Content-Type": "application/json",
                    "Authorization": bearer,
                }
#                ATTENDEES = []
#                for attendee in event.registration_ids.filtered(
#                        lambda att: att.state in ['open']):
#                    att_partner = attendee.partner_id
#                    ATTENDEES.append({
#                        "identity": {
#                            "user": {
#                                "id": att_partner.kerndata_key,
#                                "displayName": att_partner.name,
#                                "identityProvider": "AAD",
#                            }
#                        },
#                        "role": "attendee",  # presenter, attendee
#                        "upn": att_partner.email,
#                    })

#                organizer_id = user.partner_id.kerndata_key
                BODY = {
                    "startDateTime": start_time,
                    "endDateTime": end_time,
                    "subject": event.name,
                    #                   "participants": {
                    #                        "organizer": {
                    #                            "identity": {
                    #                                "user": {
                    #                                    "id": organizer_id,
                    #                                    "displayName": user.name,
                    #                                    "identityProvider": "AAD",
                    #                                },
                    #                            },
                    #                            "role": "presenter",
                    #                            "upn": user.email,
                    #                        },
                    #                        # "attendees": ATTENDEES,
                    #                    }
                }
                meeting_response = requests.request(
                    "POST",
                    "https://graph.microsoft.com/v1.0/me/onlineMeetings",
                    headers=headers, json=BODY, timeout=10)
                if meeting_response.status_code == 201:
                    meet_vals = meeting_response.json()
                    event.ms_meeting_id = meet_vals.get('id')
                    event.ms_meeting_url = meet_vals.get('joinUrl')
                else:
                    raise UserError(_(
                        "Please Authenticate with Microsoft Meeting. {}"
                    ).format(meeting_response.text))
            event_mail_obj.create({
                'event_id': event.id,
                'notification_type': 'mail',
                'template_ref': '%s,%i' % (template._name, template.id),
                'interval_nbr': 1,
                'interval_unit': 'days',
                'interval_type': 'before_event',
            })
        return True
