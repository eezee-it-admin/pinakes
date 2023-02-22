# -*- encoding: utf-8 -*-
# Copyright 2022      Eezee-IT (<http://www.eezee-it.com>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
from odoo.tests import TransactionCase


class TestMailThread(TransactionCase):

    def setUp(self):
        super(TestMailThread, self).setUp()
        config_parameter_env = self.env["ir.config_parameter"].sudo()
        self.set_param = config_parameter_env.set_param
        self.set_param('mail.catchall.domain', 'eezee-it.com')

    def test_clean_mail(self):
        mail_env = self.env['mail.thread']
        domain_catchall = mail_env.get_catchall_domain()
        res1 = mail_env.get_clean_mail('jobs@beopen.be', domain_catchall)
        res2 = mail_env.get_clean_mail('jobs@beopen.be', 'eezee-it.com')
        res3 = mail_env.get_clean_mail('jobs@beopen.be', 'beopen-be')
        self.assertEqual(res1, 'jobs-at-beopen-be@eezee-it.com')
        self.assertEqual(res2, 'jobs-at-beopen-be@eezee-it.com')
        self.assertEqual(res3, 'jobs-at-beopen-be@beopen-be')
