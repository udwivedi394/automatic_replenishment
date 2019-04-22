from django.shortcuts import render
from django.views import View

from automatic_replenishment_system.retail_core.models import BrandModel


class ExistingBrandsView(View):
    def get(self, request):
        existing_brands = BrandModel.objects.all().values()
        context = {
            'title': 'Existing Brands',
            'brands': existing_brands
        }
        return render(request, 'brand/brand_list.html', context)
