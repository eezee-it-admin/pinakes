# Copyright 2021 Eezee-IT (<http://www.eezee-it.com>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
{
    "name": "Pinakes Base",
    "version": "16.0.0.0.18",
    "author": "Eezee-It",
    "category": "Services",
    "license": "LGPL-3",
    "summary": "Pinakes Base",
    "depends": [
        "base_geolocalize",
        "contacts",
        "website_crm_partner_assign",
        "website_partner",
        "product",
        "l10n_be_reports",
        "stock",
    ],
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "views/res_company_view.xml",
        "views/partner_view.xml",
        "views/product_template_view.xml",
        "views/product_view.xml",
        "views/product_author_view.xml",
        "views/publication_lang_view.xml",
        "views/menuitems.xml",
    ],
    "application": True,
}
