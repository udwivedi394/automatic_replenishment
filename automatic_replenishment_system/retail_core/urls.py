from django.urls import path

from automatic_replenishment_system.retail_core.views.create_brand_view import CreateBrandView

urlpatterns = [path('brand_one_time_setup-create/', CreateBrandView.as_view(), name='create_brand'),
               ]
