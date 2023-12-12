# -*- encoding: utf-8 -*-
##############################################################################
#
#    Copyright BeOpen-It (C) 2019
#    Author: BeOpen-It <info@beopen.be>
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
##############################################################################
{
    "name": "Microsoft Teams Integration with Odoo Event",
    "version": "16.0.1.0.0",
    "author": "Eezee (BeOpen-IT)",
    "website": "https://beopen.be",
    "summary": "Create Microsoft Teams Meetings from Odoo Event",
    "category": "Marketing/Events",
    "license": "LGPL-3",
    "depends": ["event"],
    "data": [
        "data/mail_data.xml",
        "views/res_users_view.xml",
        "views/event_view.xml",
        "views/res_config_settings_view.xml",
    ],
    "images": ["static/description/banner.png"],
    "installable": True,
    "price": 250,
    "currency": "EUR",
}
