odoo.define('pinakes_website.s_dynamic_snippet_products_options', function (require) {
    'use strict';

    const options = require('web_editor.snippets.options');
    const dynamicSnippetProductsOptions = require('website_sale.s_dynamic_snippet_products_options');

    const pinakesDynamicSnippetProductsOptions = dynamicSnippetProductsOptions.extend({
        /**
         * @override
         * @private
         */
        _setOptionsDefaultValues: function () {
            this._setOptionValue('productCategoryId', 'all');
            this._setOptionValue('productType', 'product_product');
            this._super.apply(this, arguments);
        },
    });
    options.registry.dynamic_snippet_products = pinakesDynamicSnippetProductsOptions;
    return pinakesDynamicSnippetProductsOptions;
});
