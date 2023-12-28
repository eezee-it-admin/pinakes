odoo.define('pinakes_website.hide_cant_be_sold', function(require) {
    'use strict';

    var publicWidget = require('web.public.widget');

    publicWidget.registry.ProductDetailBehavior = publicWidget.Widget.extend({
        selector: '.js_product',

        init: function(parent) {
            if (this.$el.hasClass('product_not_for_sale')) {
                this.$('.product_price, .css_quantity, #add_to_cart_wrap, #product_option_block').hide();
            }
            return this._super.apply(this, arguments);
        },
    });
});
