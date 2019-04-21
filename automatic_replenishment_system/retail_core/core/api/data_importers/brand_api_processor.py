from django.db import transaction

from automatic_replenishment_system.retail_core.core.api.data_importers.serializers import BrandInputSerializer
from automatic_replenishment_system.retail_core.core.constants import BrandFilesConstants
from automatic_replenishment_system.retail_core.models import BrandModel, ProductModel, StoreModel, WarehouseModel, \
    StoreWarehouseMappingModel


class BrandInputData:
    def __init__(self):
        self.name = None
        self.ranking_model = None
        self.products = None
        self.stores = None
        self.warehouses = None


class BrandCreationRequestProcessor:
    def process_post_request_parameters(self, request):
        request_data = BrandInputData()
        serializer = BrandInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        request_data.name = serializer.validated_data['name']
        request_data.ranking_model = serializer.validated_data['ranking_model']
        request_data.stores = serializer.validated_data['stores']
        request_data.products = serializer.validated_data['products']
        request_data.warehouses = serializer.validated_data['warehouses']
        return request_data


class BrandCreationProcessor:
    @transaction.atomic()
    def execute(self, request):
        data = BrandCreationRequestProcessor().process_post_request_parameters(request)
        brand = self._get_brand(data.name, data.ranking_model)
        self._save_models([brand], BrandModel)
        products = self._get_products(data.products, brand)
        stores = self._get_stores(data.stores, brand)
        self._save_models(products, ProductModel)
        self._save_models(stores, StoreModel)
        warehouses = self._get_warehouses(data.warehouses, brand)
        self._save_models(warehouses, WarehouseModel)
        store_warehouses = self._get_store_warehouses(data.warehouses, warehouses, stores)
        self._save_models(store_warehouses, StoreWarehouseMappingModel)

    def _get_brand(self, name, ranking_model):
        brand = BrandModel(name=name, ranking_model=ranking_model)
        return brand

    def _get_products(self, products, brand):
        product_list = list()
        for product in products:
            product_code = product[BrandFilesConstants.PRODUCT_CODE]
            product_model = ProductModel(product_code=product_code, brand_model=brand)
            product_list.append(product_model)
        return product_list

    def _get_stores(self, stores, brand):
        stores_list = list()
        for store in stores:
            store_code = store['Store_Code']
            store_model = StoreModel(store_code=store_code, brand_model=brand)
            stores_list.append(store_model)
        return stores_list

    def _get_store_warehouses(self, store_warehouses, warehouses, stores):
        store_warehouse_list = list()
        store_map = self._gen_store_map(stores)
        warehouse_map = self.gen_warehouse_map(warehouses)
        for store_warehouse_row in store_warehouses:
            warehouse_code = store_warehouse_row[BrandFilesConstants.WAREHOUSE_CODE]
            store_code = store_warehouse_row[BrandFilesConstants.STORE_CODE]
            store = store_map[store_code]
            warehouse = warehouse_map[warehouse_code]
            store_warehouse_model = StoreWarehouseMappingModel(store=store, warehouse=warehouse)
            store_warehouse_list.append(store_warehouse_model)
        return store_warehouse_list

    def _save_models(self, models, model_class):
        model_class.objects.bulk_create(models, batch_size=1000)

    def _gen_store_map(self, stores):
        store_map = dict()
        for store in stores:
            store_map[store.store_code] = store
        return store_map

    def gen_warehouse_map(self, warehouses):
        warehouse_map = dict()
        for warehouse in warehouses:
            warehouse_map[warehouse.warehouse_code] = warehouse
        return warehouse_map

    def _get_warehouses(self, store_warehouses, brand):
        warehouse_code_set = set()
        for store_warehouse in store_warehouses:
            warehouse_code_set.add(store_warehouse[BrandFilesConstants.WAREHOUSE_CODE])
        warehouse_list = list()
        for warehouse_code in warehouse_code_set:
            warehouse = WarehouseModel(warehouse_code=warehouse_code, brand_model=brand)
            warehouse_list.append(warehouse)
        return warehouse_list
