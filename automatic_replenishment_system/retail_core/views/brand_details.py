from django.db import transaction
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views import View

from automatic_replenishment_system.retail_core.forms import BrandViewForm
from automatic_replenishment_system.retail_core.models import BrandModel


class BrandDetailsView(View):
    BRAND_FORM_PREFIX = 'brand'

    def get(self, request, brand_id):
        brand_model = self._get_brand_model(brand_id)
        if not brand_model:
            return HttpResponse('Brand Does not exists! Brand Id: {}'.format(brand_id))
        brand_view_form = BrandViewForm(prefix=self.BRAND_FORM_PREFIX)
        return self._render(request, brand_view_form, brand_model)

    def post(self, request, brand_id):
        brand_view_form = BrandViewForm(request.POST, request.FILES, prefix=self.BRAND_FORM_PREFIX)
        brand_model = self._get_brand_model(brand_id)
        if brand_view_form.is_valid():
            brand_ranking_model = self._get_brand_ranking_model(brand_view_form)
            transaction.on_commit(
                lambda: self._update_brand(brand_model, brand_ranking_model))
            return HttpResponseRedirect(reverse('existing_brands', kwargs={}))
        else:
            print('Invalid Data in form')
        return self._render(request, brand_view_form, brand_model)

    def _render(self, request, brand_view_form, brand_model):
        context = {
            'brand_name': brand_model.name,
            'current_ranking_model': brand_model.ranking_model,
            'brand_view_form': brand_view_form,
        }
        template_name = 'brand/view_brand.html'
        return render(request, template_name, context)

    def _get_brand_ranking_model(self, brand_view_form):
        ranking_model = self._get_parameter(brand_view_form, 'ranking_model')
        return ranking_model

    def _update_brand(self, brand_model, brand_ranking_model):
        brand_model.ranking_model = brand_ranking_model
        brand_model.save()

    def _get_brand_model(self, brand_id):
        brand_model = BrandModel.objects.filter(id=brand_id).first()
        return brand_model

    def _get_parameter(self, form, field_name):
        return form.cleaned_data.get(field_name)
