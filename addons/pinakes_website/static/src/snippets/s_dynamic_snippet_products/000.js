odoo.define('pinakes_website.s_dynamic_snippet_products', function (require) {
    'use strict';

    const publicWidget = require('web.public.widget');
    const DynamicSnippetProducts = require('website_sale.s_dynamic_snippet_products');

    const PinakesDynamicSnippetProducts = DynamicSnippetProducts.extend({
        /**
         * Method to be overridden in child components in order to provide a search
         * domain if needed.
         * @override
         * @private
         */
        _getSearchDomain() {
            let searchDomain = this._super(...arguments);
            searchDomain.push(...this._getCategorySearchDomain());
            searchDomain.push(...this._getTagSearchDomain());
            const productNames = this.$el.get(0).dataset.productNames;
            if (productNames) {
                const nameDomain = [];
                for (const productName of productNames.split(',')) {
                    // Ignore empty names
                    if (!productName.length) {
                        continue;
                    }
                    // Search on name, internal reference and barcode.
                    if (nameDomain.length) {
                        nameDomain.unshift('|');
                    }
                    nameDomain.push(...[
                        '|', '|', ['name', 'ilike', productName],
                        ['default_code', '=', productName],
                        ['barcode', '=', productName],
                    ]);
                }
                searchDomain.push(...nameDomain);
            }

            let productTypeOpt = this.$el.get(0).dataset.productType;

            if (productTypeOpt === 'product_template') {
                const uniqueProductIds = this._fetchUniqueProductIdsSync(searchDomain);
                searchDomain.push(['id', 'in', uniqueProductIds]);
            }

            return searchDomain;
        },

        _fetchUniqueProductIdsSync(searchDomain) {
            let uniqueProductIds = [];
            $.ajax({
                url: '/product/filter_unique',
                method: 'POST',
                contentType: "application/json",
                async: false,
                data: JSON.stringify({
                    jsonrpc: "2.0",
                    method: "call",
                    params: {search_domain: searchDomain},
                    id: new Date().getTime()
                }),
                dataType: 'json',
                success: function (data) {
                    uniqueProductIds = data.result.ids;
                },
                error: function (error) {
                    console.error("Error during RPC call:", error);
                }
            });
            return uniqueProductIds;
        },
    })
    publicWidget.registry.pinakes_dynamic_snippet_products = PinakesDynamicSnippetProducts;
    return PinakesDynamicSnippetProducts;
});
