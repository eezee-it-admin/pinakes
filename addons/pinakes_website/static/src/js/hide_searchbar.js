odoo.define('pinakes_website.hide_searchbar_script', function(require) {
    'use strict';

    var publicWidget = require('web.public.widget');

    publicWidget.RootWidget.include({
        init: function(parent) {
            this._super.apply(this, arguments);
            var path = window.location.pathname;
            if (path === '/shop' || path.startsWith('/shop?') || path.startsWith('/shop/category')) {
                $('body').addClass('shop-page');
            }
        },
    });
});
