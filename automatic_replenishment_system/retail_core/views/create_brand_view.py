from django.db import transaction
from django.forms import formset_factory
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views import View

from automatic_replenishment_system.retail_core.forms import BrandForm, StoreForm, ProductForm, WarehouseForm


class CreateBrandView(View):
    BRAND_FORM_PREFIX = 'brand'
    CONFIG_FORM_PREFIX = 'config'

    def get(self, request):
        brand_form = BrandForm(prefix=self.BRAND_FORM_PREFIX)
        product_form = ProductForm(prefix=self.BRAND_FORM_PREFIX)
        store_form = StoreForm(prefix=self.BRAND_FORM_PREFIX)
        warehouse_form = WarehouseForm(prefix=self.BRAND_FORM_PREFIX)
        return self._render(request, brand_form, product_form, store_form, warehouse_form)

    def post(self, request):
        file_name_errors = None
        csv_name_errors = None
        report_form = ReportForm(request.POST, request.FILES, prefix=self.BRAND_FORM_PREFIX)
        config_form = ReportConfigForm(request.POST, prefix=self.CONFIG_FORM_PREFIX)
        brand_form_set = self._get_brand_formset()(request.POST, request.FILES)

        if report_form.is_valid() and config_form.is_valid() and brand_form_set.is_valid():
            file_name_errors, csv_name_errors = self._validate_data(brand_form_set, report_form)
            if file_name_errors is None and csv_name_errors is None:
                report_model = report_form.save()
                config_model = self._save_model_with_report_foreign_key(config_form, report_model)
                for brand_form in brand_form_set:
                    valid_brand = self._save_brand(brand_form, report_model)
                    if not valid_brand:
                        break
                else:
                    kwargs = {
                        'report_id': report_model.id
                    }
                    ReviewSaver(report_model).save_reviews()
                    transaction.on_commit(lambda: self._run_processes(report_model, config_model))
                    return HttpResponseRedirect(reverse('report_details', kwargs=kwargs))
        else:
            print('Invalid Data in form')
        return self._render(request, report_form, config_form, brand_form_set, file_name_errors, csv_name_errors)

    def _render(self, request, brand_form, product_form, store_form, warehouse_form, file_name_errors=None,
                csv_name_errors=None):
        context = {
            'brand_form': brand_form,
            'product_form': product_form,
            'store_form': store_form,
            'warehouse_form': warehouse_form,
            'file_name_errors': file_name_errors,
            'csv_name_errors': csv_name_errors,
        }
        template_name = 'brand/create_brand.html'
        return render(request, template_name, context)

    def _get_brand_formset(self):
        return formset_factory(BrandModelForm, extra=1, can_delete=True)

    def _save_model_with_report_foreign_key(self, form, report_model):
        form_model = form.save(commit=False)
        form_model.report_model = report_model
        form_model.save()
        return form_model

    def _save_brand(self, brand_form, report_model):
        valid_brand = True
        if not brand_form.is_valid():
            print('Invalid brand form')
            valid_brand = False
        elif not brand_form.cleaned_data.get('name'):
            print('Empty Brand, no need to save')
        else:
            self._save_model_with_report_foreign_key(brand_form, report_model)
        return valid_brand

    def _run_processes(self, report_model, config_model):
        ReportProcessManager(report_model, config_model).execute()

    def _validate_data(self, brand_form_set, report_form):
        file_name_errors, csv_name_errors = NameDuplicateValidator().validate_report_screen(brand_form_set,
                                                                                            report_form)
        return file_name_errors, csv_name_errors
