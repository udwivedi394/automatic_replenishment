from django.urls import path

from automatic_replenishment_system.retail_core.views.brand_details import BrandDetailsView
from automatic_replenishment_system.retail_core.views.brand_list import ExistingBrandsView
from automatic_replenishment_system.retail_core.views.create_brand_view import CreateBrandView
from automatic_replenishment_system.retail_core.views.download_orders import ExistingOrders
from automatic_replenishment_system.retail_core.views.generate_order import GenerateOrderView

urlpatterns = [path('brand-create/', CreateBrandView.as_view(), name='create_brand'),
               path('existing/', ExistingBrandsView.as_view(), name='existing_brands'),
               path('details/<int:brand_id>', BrandDetailsView.as_view(), name='view_brand'),
               path('generate-order/<int:brand_id>', GenerateOrderView.as_view(), name='generate_order'),
               path('view-orders/<int:brand_id>', ExistingOrders.as_view(), name='download_order')
               ]
