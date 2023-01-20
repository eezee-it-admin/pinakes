# -*- coding: utf-8 -*-
# #############################################################################
#
#    Copyright Eezee-It (C) 2017-2020
#    Author: Eezee-It <info@eezee-it.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Lesser General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Lesser General Public License for more details.
#
#    You should have received a copy of the GNU Lesser General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################
{
    "name": "FTP / HTTP Client",
    "version": '15.0.0.1.2',
    "application": False,
    "license": 'LGPL-3',
    "category": 'Tools',
    "summary": """
    FTP / HTTP Client
    """,
    "author": "Eezee-It",
    "support": "support@eezee-it.com",
    "website": 'http://www.eezee-it.com',
    "depends": [
        'base'
    ],
    "data": [
        'security/ftp_security.xml',
        'security/ir.model.access.csv',
        'views/network_client.xml',
        'views/network_client_parameter.xml',
        'views/network_client_line.xml',
        'views/ir_attachment.xml',
        'views/ir_logging.xml',
        'views/menu.xml',
    ],
    "external_dependencies": {
        'python': [
            'pandas', 'pysftp'
        ],
    },
    "demo": [],
    "qweb": [],
    "post_load": None,
    "pre_init_hook": None,
    "post_init_hook": None,
    "uninstall_hook": None,
    "auto_install": False,
    "installable": True,
}
