# Copyright 2022  Eezee-IT (<http://www.eezee-it.com>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import models, api


class MailMail(models.Model):
    _name = 'mail.mail'
    _inherit = ['mail.mail']

    def regenerate_standard_mail(self, reply):
        if "-at-" in reply:
            new_mail = ""
            # Get Name from adresse mail like
            # My Company <my.company@eezee-it.com>
            name = ""
            no_name = reply.split("<")
            if no_name:
                reply = no_name[-1].replace(">", "")
                name = no_name[0].replace('"', '')
            tmp_mail = reply.split("@")
            if tmp_mail:
                # delete current domain
                tmp_mail = tmp_mail[0]
                # regenerate domain from something like my-domain-at-eezee-be
                tmp_mail = tmp_mail.replace("-at-", "@")
                # replace last - by a .
                last_point = tmp_mail.rfind("-")
                new_mail = \
                    tmp_mail[:last_point] + "." + tmp_mail[last_point + 1:]
                if name:
                    new_mail = name + " <" + new_mail + ">"
            return new_mail
        else:
            return False

    @api.model
    def create(self, values):
        if values.get("reply_to", False):
            if "-at-" in values["reply_to"]:
                new_mail = self.regenerate_standard_mail(values['reply_to'])
                if new_mail:
                    values['reply_to'] = new_mail

        return super(MailMail, self).create(values)

    def send(self, auto_commit=False, raise_exception=False):
        for record in self:
            if record.reply_to:
                if "-at-" in record.reply_to:
                    new_mail = self.regenerate_standard_mail(record.reply_to)
                    record.reply_to = new_mail

        return super(MailMail, self).send(auto_commit, raise_exception)
