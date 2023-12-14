# Copyright 2023 Eezee-IT (<http://www.eezee-it.com>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
from odoo import models, fields
import requests
from requests_toolbelt.multipart.encoder import MultipartEncoder
import xml.etree.ElementTree as ET
import base64


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    booxtream_link = fields.Char(string='Link To BooXtream')

    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()
        for rec in self:
            for line in rec.order_line:
                if self.is_digital_book(line.name):
                    self._get_confirmation_template()
                    self.booxtream_link = self.generate_link(line.product_template_id, self.partner_id)
                else:
                    super(SaleOrder, self)._get_confirmation_template()
                break
        return res

    def is_digital_book(self, name):
        if 'digitaal' in name.lower():
            return True
        return False

    def generate_link(self, product_template_id, partner_id):
        url = 'https://service.booxtream.com/booxtream.xml'
        headers = {'Content-Type': 'multipart/form-data'}

        epub_data = base64.b64decode(product_template_id.epub_file)
        epub_name = str(product_template_id.epub_name)

        multipart_data = MultipartEncoder(
            fields={
                'epubfile': ((epub_name + ".epub"), epub_data, 'application/epub+zip'),
                'customeremailaddress': str(partner_id.email),
                'customername': str(partner_id.name),
                'languagecode': '1033',
                'expirydays': '30',
                'downloadlimit': '5',
                'referenceid': str(product_template_id.id)
            }
        )

        headers['Content-Type'] = multipart_data.content_type

        response = requests.post(url, headers=headers, data=multipart_data,
                                 auth=('politeiatest', 'cY1gAp4sKmewkAAx0BJcJcoYNUn0ZD'))

        response_xml_as_string = response.content.decode('utf-8')
        responseXml = ET.fromstring(response_xml_as_string)

        if response.status_code == 200:
            download_link_element = responseXml.find(".//DownloadLink")
            if download_link_element is not None:
                download_link = download_link_element.text
            else:
                raise Exception('Failed to find download link in response')
            return download_link
        else:
            raise Exception('Failed to generate BooXtream link')

    def _get_digital_confirmation_template(self):
        return self.env.ref('pinakes_api.mail_template_sale_confirmation', raise_if_not_found=False)

    def _send_order_confirmation_mail(self):
        if not self:
            return

        for sale_order in self:
            is_digital = any(self.is_digital_book(line.name) for line in sale_order.order_line)

            if is_digital:
                mail_template = sale_order._get_digital_confirmation_template()
            else:
                mail_template = sale_order._get_confirmation_template()

            if not mail_template:
                continue

            sale_order.with_context(force_send=True).message_post_with_template(
                mail_template.id,
                composition_mode='comment',
                email_layout_xmlid='mail.mail_notification_layout_with_responsible_signature',
            )
