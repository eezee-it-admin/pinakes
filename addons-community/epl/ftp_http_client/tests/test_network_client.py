# Copyright 2017-2023 Eezee-IT (<https://www.eezee-it.com>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError


class TestNetworkClient(TransactionCase):
    """
    Tests for network.client (FTP AND HTTP)
    """

    def setUp(self):
        super(TestNetworkClient, self).setUp()
        self.client_obj = self.env['network.client']
        self.client_line_obj = self.env['network.client.line']
        self.parameters_obj = self.env['network.client.parameter']
        self.attachment_obj = self.env['ir.attachment']
        self.http_client = self.client_obj.create({
            'client_type': 'http',
            'name': "Test HTTP Client",
            'host': "test.host",
            'request_type': 'post',
        })

        self.ftp_client = self.client_obj.create({
            'client_type': 'ftp',
            'name': "Test FTP Client",
            'host': "test.host",
        })

        self.http_client_line = self.client_line_obj.create({
            'name': 'HTTP Line',
            'client_id': self.http_client.id
        })

        self.ftp_client_line = self.client_line_obj.create({
            'name': 'FTP Line',
            'client_id': self.ftp_client.id
        })

        self.parameter_1 = self.parameters_obj.create({
            'name': 'Parameter 1',
            'value': 'Value 1',
            'client_line_id': self.http_client_line.id
        })

        self.parameter_2 = self.parameters_obj.create({
            'name': 'Parameter 2',
            'value': 'Value 2',
            'client_line_id': self.http_client_line.id
        })

    def test_get_params(self):
        """
        Test function for getting HTTP Client's parameters
        """
        params = self.http_client_line.get_params()
        expected_params = {
            self.parameter_1.name: self.parameter_1.value,
            self.parameter_2.name: self.parameter_2.value
        }

        self.assertEqual(params, expected_params, "Wrong parameters returned")

        self.parameter_1.unlink()
        self.parameter_2.unlink()
        params = self.http_client_line.get_params()
        expected_params = {}

        self.assertEqual(params, expected_params, "Wrong parameters returned")

    def test_client_line_attach_file(self):
        """
        Test function for saving content as an attachment for Network Client
        Line
        """

        content = "Test file content"
        attachment_id = self.attachment_obj.search([
            ('res_id', '=', self.ftp_client_line.id)
        ]).id
        expected_attachment_id = False

        self.assertEqual(
            attachment_id, expected_attachment_id, "No attachment expected")

        expected_attachment_id = self.ftp_client_line.attach_file(content).id
        attachment_id = self.attachment_obj.search([
            ('res_id', '=', self.ftp_client_line.id)
        ]).id
        self.assertEqual(
            attachment_id, expected_attachment_id, "File was not attached")

    def test_client_line_action_attachments(self):
        """
        Test action returned
        """
        content = "Test file content"
        attachments = self.attachment_obj.search([
            ('res_model', '=', 'network.client.line'),
            ('res_id', '=', self.ftp_client_line.id)
        ])
        attachments.unlink()
        line_attachment_id = self.ftp_client_line.attach_file(content).id

        expected_action_domain = [
            ('id', 'in', [line_attachment_id])]
        action = self.ftp_client_line.action_line_attachments()
        action_domain = action.get('domain', [('id', 'in', [])])
        action_domain_ids = sorted(action_domain[0][2])
        action_domain = [('id', 'in', action_domain_ids)]
        self.assertEqual(
            action_domain, expected_action_domain,
            "Action with wrong domain returned")

    def test_client_action_attachments(self):
        """
        Test actions for checking
            1) All attachments for network client and lines
            2) All attachments for network client lines
        """
        content = "Test file content"
        attachments = self.attachment_obj.search([
            ('res_model', 'in', ['network.client', 'network.client.line']),
            ('res_id', '=', True)
        ])
        attachments.unlink()
        line_attachment_id = self.ftp_client_line.attach_file(content).id
        ftp_attachment_id = self.attachment_obj.create({
            'name': 'My Attachment',
            'res_model': 'network.client',
            'res_id': self.ftp_client.id,
        }).id

        client = self.ftp_client.with_context({'all_attachments': True})
        expected_action_domain = [
            ('id', 'in', sorted([line_attachment_id, ftp_attachment_id]))]

        action = client.action_attachments()
        action_domain = action.get('domain', [('id', 'in', [])])
        action_domain_ids = sorted(action_domain[0][2])
        action_domain = [('id', 'in', action_domain_ids)]
        self.assertEqual(
            action_domain, expected_action_domain,
            "Action with wrong domain returned")

        client = self.ftp_client.with_context({'line_attachments': True})
        expected_action_domain = [
            ('id', 'in', [line_attachment_id])]

        action = client.action_attachments()
        action_domain = action.get('domain', [])

        self.assertEqual(
            action_domain, expected_action_domain,
            "Action with wrong domain returned")

    def test_ftp_client_timeout(self):
        """
        Test network.client's Timeout' field accepted values [1-9999]
        """
        with self.assertRaises(ValidationError):
            self.ftp_client.write({
                'timeout': 0,
            })
        with self.assertRaises(ValidationError):
            self.ftp_client.write({
                'timeout': 10000,
            })

    def test_compute_client_type(self):
        main_client_type = self.ftp_client.client_type
        line_client_type = self.ftp_client_line.client_type

        self.assertEqual(
            main_client_type, line_client_type, "Wrong client type")

        self.ftp_client_line.client_id = self.http_client
        self.ftp_client_line.onchange_client_id()

        main_client_type = self.http_client.client_type
        line_client_type = self.http_client_line.client_type

        self.assertEqual(
            main_client_type, line_client_type, "Wrong client type")

    def test_load_from_name1(self):
        """
        Test the load_from_name
        :return:
        """
        names = [
            'HTTP Line',
            'FTP Line',
        ]
        client_line_obj = self.client_line_obj
        msg = "The load_from_name() function doesn't work properly"
        for name in names:
            self.assertEqual(client_line_obj.load_from_name(name), True, msg)
        for name in ['Titi toto', 'tutu']:
            self.assertEqual(client_line_obj.load_from_name(name), False, msg)
