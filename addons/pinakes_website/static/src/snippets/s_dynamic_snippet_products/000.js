odoo.define('pinakes_website.s_dynamic_snippet_products', function (require) {
    'use strict';

    const publicWidget = require('web.public.widget');
    const DynamicSnippetProducts = require('website_sale.s_dynamic_snippet_products');
    let processingDone = false;


    const PinakesDynamicSnippetProducts = DynamicSnippetProducts.extend({
        init: function () {
            this._super.apply(this, arguments);
            this._hideSnippetsAndShowSpinner();
        },

        _hideSnippetsAndShowSpinner: function () {
            if (!processingDone) {
                const sections = document.querySelectorAll('section[data-snippet="s_dynamic_snippet_products"]');

                const createSpinner = () => {
                    const spinnerContainer = document.createElement('div');
                    spinnerContainer.classList.add('d-flex', 'justify-content-center', 'align-items-center');
                    spinnerContainer.style.height = '50px';
                    spinnerContainer.innerHTML = '<div class="spinner-border text-primary" role="status"><span class="sr-only">Loading...</span></div>';
                    return spinnerContainer;
                };

                const addSpinner = (section) => {
                    const spinnerContainer = createSpinner();
                    section.classList.add('hide_product_snippet');
                    section.insertAdjacentElement('afterend', spinnerContainer);

                    setTimeout(() => {
                        spinnerContainer.remove();
                        section.classList.remove('hide_product_snippet');
                    }, 9000);
                };

                sections.forEach(section => {
                    addSpinner(section);
                });

                processingDone = true;
            }
        },


        /**
         * Method to be overridden in child components in order to provide a search
         * domain if needed.
         * @override
         * @private
         */
        _getSearchDomain() {
            let searchDomain = this._super(...arguments);
            searchDomain.push(...this._getCategorySearchDomain());
            const productNames = this.$el.get(0).dataset.productNames;
            if (productNames) {
                const nameDomain = [];
                for (const productName of productNames.split(',')) {
                    if (!productName.length) {
                        continue;
                    }
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
            searchDomain.push(...this._getTagSearchDomain());

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
    const PinakesDynamicSnippetProductsCard = publicWidget.registry.dynamic_snippet_products_cta.extend({

        read_events: {
            'click .js_add_cart': '_onClickAddToCart',
            'click .js_remove': '_onRemoveFromRecentlyViewed',
            'click .show_variants': '_onClickShowVariants',
        },
        /**
         * @param {OdooEvent} ev
         */
        async _onClickShowVariants(ev) {
            const $card = $(ev.currentTarget).closest('.card');
            const product_id = $card.find('input[data-product-id]').data('product-id');
            $('#variants_modal_' + product_id).modal('show');
        }

    });

    publicWidget.registry.pinakes_dynamic_snippet_products = PinakesDynamicSnippetProducts;
    publicWidget.registry.dynamic_snippet_products_cta = PinakesDynamicSnippetProductsCard;
    return PinakesDynamicSnippetProducts;
});
