# Copyright 2022  Eezee-IT (<http://www.eezee-it.com>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
from odoo.tests import TransactionCase


class TestMailMail(TransactionCase):

    def setUp(self):
        super(TestMailMail, self).setUp()

    def test_create_mail(self):
        mail_obj = self.env['mail.mail'].create({
            'subject': 'Odoo common test',
            'reply_to': 'jobs-at-beopen-be@eezee-it.com',
            'body_html': '<p>Test</p>',
            'email_to': 'no_reply@eezee-it.com',
            'email_from': 'jobs-at-beopen-be@eezee-it.com',
            'auto_delete': False,
            'mail_server_id': False
        })
        self.assertTrue(mail_obj)
        self.assertEqual(mail_obj.reply_to, 'jobs-at-beopen-be@eezee-it.com <jobs@beopen.be>')
        self.assertEqual(mail_obj.email_from, 'jobs-at-beopen-be@eezee-it.com')
