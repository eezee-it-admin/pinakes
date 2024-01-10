odoo.define('pinakes_website.reeds_besteld', function (require) {
    'use strict';

    var publicWidget = require('web.public.widget');

    publicWidget.registry.TagsFilter = publicWidget.Widget.extend({
        selector: '#product_details',
        events: {
            'change .product_id': '_onVariantRadioChange',
        },

        start: function () {
            this._super.apply(this, arguments);
        },

        _onVariantRadioChange: function (ev) {
            var selectedVariantId = parseInt(ev.target.value);

            this._rpc({
                model: 'product.product',
                method: 'read',
                args: [[selectedVariantId], ['display_name']],
            }).then(function (result) {
                if (result.length > 0) {
                    var variantName = result[0].display_name;
                    console.log(variantName);

                    var reedsBesteldElement = document.getElementById('reeds_besteld');

                    if (variantName.toLowerCase().includes('digitaal')) {
                        reedsBesteldElement.classList.remove('d-none');
                    } else {
                        reedsBesteldElement.classList.add('d-none');
                    }
                }
            });
        },
    });
});