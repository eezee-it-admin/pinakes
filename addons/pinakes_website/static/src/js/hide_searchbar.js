odoo.define('pinakes_website.custom_script', function(require) {
    'use strict';

    var publicWidget = require('web.public.widget');

    publicWidget.RootWidget.include({
        start: function() {
            this._super.apply(this, arguments);
            if (window.location.pathname.startsWith('/shop')) {
                $('body').addClass('shop-page');
            }
        },
    });
});
