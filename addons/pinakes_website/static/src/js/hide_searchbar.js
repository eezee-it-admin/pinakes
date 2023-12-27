odoo.define('pinakes_website.hide_searchbar_script', function(require) {
    'use strict';

    var publicWidget = require('web.public.widget');

    publicWidget.RootWidget.include({
        init: function(parent) {
            this._super.apply(this, arguments);
            if (window.location.pathname.startsWith('/shop')) {
                $('body').addClass('shop-page');
            }
        },
    });
});

