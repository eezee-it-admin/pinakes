odoo.define('pinakes_website.CustomVariantMixin', function (require) {
    'use strict';

    var VariantMixin = require('website_sale.VariantMixin');

    const originalOnChangeCombination = VariantMixin._onChangeCombination;

    VariantMixin._onChangeCombination = function (ev, $parent, combinationData) {
        var $isbnElement = $('#product_isbn');
        if ($isbnElement.length) {
            $isbnElement.text(combinationData.isbn);
        }
        originalOnChangeCombination.apply(this, [ev, $parent, combinationData]);
    };
});
