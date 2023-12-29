odoo.define('pinakes_website.hide_searchbar_script', function(require) {
    'use strict';

    var publicWidget = require('web.public.widget');

    publicWidget.RootWidget.include({
        init: function(parent) {
            this._super.apply(this, arguments);
            var path = window.location.pathname;

            if (path === '/shop' || path.startsWith('/shop?') || path.startsWith('/shop/category') ||
                path === '/fr_BE/shop' || path.startsWith('/fr_BE/shop?') || path.startsWith('/fr_BE/shop/category') ||
                path === '/en_UK/shop' || path.startsWith('/en_UK/shop?') || path.startsWith('/en_UK/shop/category') ||
                path === '/en_US/shop' || path.startsWith('/en_US/shop?') || path.startsWith('/en_US/shop/category')) {
                $('body').addClass('shop-page');
            }
        },
    });
});
