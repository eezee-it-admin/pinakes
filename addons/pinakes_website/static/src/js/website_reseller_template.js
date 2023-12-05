odoo.define('pinakes_website.smooth_scroll', function (require) {
    'use strict';

    var publicWidget = require('web.public.widget');

    publicWidget.registry.SmoothScroll = publicWidget.Widget.extend({
        selector: '.smooth-scroll-table',
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

    publicWidget.registry.ResetSearch = publicWidget.Widget.extend({
        selector: '.reset-search-container',
        events: {
            'click .reset-search-button': '_onResetSearch',
        },

        start: function () {
            this._super.apply(this, arguments);
            this.$searchInput = this.$('.search-query');
            this.$resetButton = this.$('.reset-search-button');
        },

        // Reset search input and redirect
        _onResetSearch: function () {
            this.$searchInput.val('');
            var baseUrl = window.location.href.split('?')[0];
            window.location.href = baseUrl;
        },
    });
});
