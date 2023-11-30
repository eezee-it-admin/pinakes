odoo.define('pinakes_website.smooth_scroll', function (require) {
    'use strict';

    var publicWidget = require('web.public.widget');

    publicWidget.registry.SmoothScroll = publicWidget.Widget.extend({
        selector: '.smooth-scroll-table', // Updated selector
        events: {
            'click a.smooth-scroll-link': '_onSmoothScroll',
        },

        start: function () {
            this._super.apply(this, arguments);
        },

        // Smooth scroll functionality
        _onSmoothScroll: function (ev) {
            ev.preventDefault();
            var target = $(ev.currentTarget).attr('href');
            var $target = $(target);
            if ($target.length) {
                $('html, body').animate({
                    scrollTop: $target.offset().top
                }, 500);
            }
        },
    });
});
