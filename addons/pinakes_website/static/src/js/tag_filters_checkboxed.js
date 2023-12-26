odoo.define('pinakes_website.tags_filter', function (require) {
    'use strict';

    var publicWidget = require('web.public.widget');

    publicWidget.registry.TagsFilter = publicWidget.Widget.extend({
        selector: '.o_wsale_products_tags_filter',
        events: {
            'change .tag-checkbox': '_onTagCheckboxChange',
        },

        start: function () {
            this._super.apply(this, arguments);
            this._updateCheckboxesFromURL();
        },

        _onTagCheckboxChange: function (ev) {
            var url = new URL(window.location);
            var selectedTags = this.$('.tag-checkbox:checked').map(function () {
                return $(this).val();
            }).get().join(',');

            if (selectedTags.length > 0) {
                url.searchParams.set('tag', selectedTags);
            } else {
                url.searchParams.delete('tag');
            }
            window.location.href = url.toString();
        },

        _updateCheckboxesFromURL: function() {
            var url = new URL(window.location);
            var selectedTags = url.searchParams.get('tag') ? url.searchParams.get('tag').split(',') : [];

            this.$('.tag-checkbox').each(function () {
                $(this).prop('checked', selectedTags.includes($(this).val()));
            });
        },
    });
});