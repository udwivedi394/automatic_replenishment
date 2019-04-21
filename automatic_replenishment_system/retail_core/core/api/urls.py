from django.urls import path

from automatic_replenishment_system.retail_core.core.api.data_importers.brand_api import BrandCreator

urlpatterns = [path('brand_one_time_setup-import/', BrandCreator.as_view(), name='brand_importer'),]
