from django.db import transaction
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views import View

from automatic_replenishment_system.retail_core.core.brand.brand_saver import BrandCreationProcessManager
from automatic_replenishment_system.retail_core.forms import BrandForm, StoreForm, ProductForm, WarehouseForm, \
    StoreStaticRankForm


class Brand:
    def __init__(self, name, ranking_model):
        self.name = name
        self.ranking_model = ranking_model


class CreateBrandView(View):
    BRAND_FORM_PREFIX = 'brand'
    PRODUCT_FORM_PREFIX = 'product'
    STORE_FORM_PREFIX = 'store'
    WAREHOUSE_FORM_PREFIX = 'warehouse'
    STATIC_RANK_FORM_PREFIX = 'static'

    def get(self, request):
        brand_form = BrandForm(prefix=self.BRAND_FORM_PREFIX)
        product_form = ProductForm(prefix=self.PRODUCT_FORM_PREFIX)
        store_form = StoreForm(prefix=self.STORE_FORM_PREFIX)
        warehouse_form = WarehouseForm(prefix=self.WAREHOUSE_FORM_PREFIX)
        static_rank_form = StoreStaticRankForm(prefix=self.STATIC_RANK_FORM_PREFIX)
        return self._render(request, brand_form, product_form, store_form, warehouse_form, static_rank_form)

    def post(self, request):
        file_name_errors = None
        csv_name_errors = None
        brand_form = BrandForm(request.POST, request.FILES, prefix=self.BRAND_FORM_PREFIX)
        product_form = ProductForm(request.POST, request.FILES, prefix=self.PRODUCT_FORM_PREFIX)
        store_form = StoreForm(request.POST, request.FILES, prefix=self.STORE_FORM_PREFIX)
        warehouse_form = WarehouseForm(request.POST, request.FILES, prefix=self.WAREHOUSE_FORM_PREFIX)
        static_rank_form = StoreStaticRankForm(request.POST, request.FILES, prefix=self.STATIC_RANK_FORM_PREFIX)

        if brand_form.is_valid() and product_form.is_valid() and store_form.is_valid() and warehouse_form.is_valid() \
            and static_rank_form.is_valid():
            if file_name_errors is None and csv_name_errors is None:
                brand = self._get_brand(brand_form)
                product_file = self._get_parameter(product_form, 'products_file')
                store_file = self._get_parameter(store_form, 'stores_file')
                warehouse_file = self._get_parameter(warehouse_form, 'warehouse_file')
                static_rank_file = self._get_parameter(static_rank_form, 'static_rank_file')
                transaction.on_commit(
                    lambda: self._create_brand(brand, product_file, store_file, warehouse_file, static_rank_file))
                return HttpResponseRedirect(reverse('existing_brands', kwargs={}))
        else:
            print('Invalid Data in form')
        return self._render(request, brand_form, product_form, store_form, warehouse_form, file_name_errors,
                            csv_name_errors)

    def _get_parameter(self, form, field_name):
        return form.cleaned_data.get(field_name)

    def _render(self, request, brand_form, product_form, store_form, warehouse_form, static_rank_form,
                file_name_errors=None,
                csv_name_errors=None):
        context = {
            'brand_form': brand_form,
            'product_form': product_form,
            'store_form': store_form,
            'warehouse_form': warehouse_form,
            'static_rank_form': static_rank_form,
            'file_name_errors': file_name_errors,
            'csv_name_errors': csv_name_errors,
        }
        template_name = 'brand/create_brand.html'
        return render(request, template_name, context)

    def _create_brand(self, brand, product_file, store_file, warehouse_file, static_rank_file):
        BrandCreationProcessManager(brand, product_file, store_file, warehouse_file, static_rank_file).execute()

    def _get_brand(self, brand_form):
        brand_name = self._get_parameter(brand_form, 'name')
        ranking_model = self._get_parameter(brand_form, 'ranking_model')
        return Brand(name=brand_name, ranking_model=ranking_model)
