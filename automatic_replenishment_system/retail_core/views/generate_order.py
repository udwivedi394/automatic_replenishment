from django.db import transaction
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views import View

from automatic_replenishment_system.retail_core.core.order.replenishment_order import ReplenishmentManager
from automatic_replenishment_system.retail_core.forms import GenerateOrderForm
from automatic_replenishment_system.retail_core.models import BrandModel


class GenerateOrderView(View):
    GENERATE_ORDER_PREFIX = 'order'

    def get(self, request, brand_id):
        brand_model = self._get_brand_model(brand_id)
        generarte_order_form = GenerateOrderForm(prefix=self.GENERATE_ORDER_PREFIX)
        return self._render(request, brand_model, generarte_order_form)

    def post(self, request, brand_id):
        file_name_errors = None
        csv_name_errors = None
        generate_order_form = GenerateOrderForm(request.POST, request.FILES, prefix=self.GENERATE_ORDER_PREFIX)
        brand_model = self._get_brand_model(brand_id)
        if generate_order_form.is_valid():
            if file_name_errors is None and csv_name_errors is None:
                transaction.on_commit(
                    lambda: self._save_data_and_generate_order(brand_model, generate_order_form))
                return HttpResponseRedirect(reverse('existing_brands', kwargs={}))
        else:
            print('Invalid Data in form')
        return self._render(request, brand_model, generate_order_form)

    def _get_parameter(self, form, field_name):
        return form.cleaned_data.get(field_name)

    def _render(self, request, brand_model, generate_order_form):
        context = {
            'brand_name': brand_model.name,
            'generate_order_form': generate_order_form,
        }
        template_name = 'order/generate_order.html'
        return render(request, template_name, context)

    def _save_data_and_generate_order(self, brand_model, generate_order_form):
        date = self._get_parameter(generate_order_form, 'date')
        bsq_file = self._get_parameter(generate_order_form, 'bsq')
        sales_transactions_file = self._get_parameter(generate_order_form, 'sales_transactions')
        store_inventory_file = self._get_parameter(generate_order_form, 'store_inventory')
        warehouse_inventory_file = self._get_parameter(generate_order_form, 'warehouse_inventory')
        ReplenishmentManager(brand_model, date, bsq_file, sales_transactions_file, store_inventory_file,
                             warehouse_inventory_file).execute()

    def _get_brand_model(self, brand_id):
        brand_model = BrandModel.objects.filter(id=brand_id).first()
        return brand_model
