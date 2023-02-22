# Copyright 2022  Eezee-IT (<http://www.eezee-it.com>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import models, api


class MailThread(models.AbstractModel):
    _inherit = "mail.thread"

    @api.model
    def get_catchall_domain(self):
        conf_obj = self.env['ir.config_parameter'].sudo()
        catchall = conf_obj.get_param('mail.catchall.domain') or ''
        return catchall

    @api.model
    def get_clean_mail(self, mail, catchall_domain):
        if not mail:
            return ""
        end_mail = ""
        # in case mail has this format
        # My Company <my.company@eezee-it.com>
        # name = ""
        no_name = mail.split("<")
        if no_name:
            mail = no_name[-1].replace(">", "")
            # name = no_name[0].replace('"', '')

        split_from = mail.split("@")
        mail_domain = split_from[-1]
        if mail_domain != catchall_domain:
            mail_domain = mail_domain.replace(".", "-")
            end_mail = \
                split_from[0] + "-at-" + mail_domain + "@" + catchall_domain
        # if name:
            # end_mail = name + " <" + end_mail + ">"
        return end_mail

    @api.model
    def message_parse(self, message, save_original=False):
        res = super(MailThread, self).\
            message_parse(message=message, save_original=save_original)
        catchall_domain = self.get_catchall_domain()
        get_from = res.get("to", False)
        get_recipients = res.get("recipients", False)

        if catchall_domain:
            end_mail = self.get_clean_mail(get_from, catchall_domain)
            if end_mail:
                res["to"] = end_mail
            # Change recipients too because Odoo search alias base on
            # recipients and not to
            end_mail_reci = self.get_clean_mail(get_recipients,
                                                catchall_domain)
            if end_mail_reci:
                res["recipients"] = end_mail_reci
        return res
