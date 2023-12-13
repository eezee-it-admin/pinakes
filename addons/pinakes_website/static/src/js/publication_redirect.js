odoo.define('pinakes_website.publication_redirect', function (require) {
    'use strict';

    var publicWidget = require('web.public.widget');

    publicWidget.registry.PublicationRedirect = publicWidget.Widget.extend({
        selector: '.oe_kanban_global_click',
        events: {
            'click': '_onRedirectToProduct',
        },

        _onRedirectToProduct: function (ev) {
            ev.preventDefault();
            var productSlug = $(ev.currentTarget).data('product-slug');
            window.location.href = productSlug;
        },
    });
});
