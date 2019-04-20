from automatic_replenishment_system.retail_core.core.api.data_importers.serializers import BrandInputSerializer
from automatic_replenishment_system.users.models import BrandModel, ProductModel, StoreModel, WarehouseModel


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
        serializer = BrandInputSerializer(data=request.POST)
        serializer.is_valid(raise_exception=True)
        request_data.name = serializer.validated_data['name']
        request_data.ranking_model = serializer.validated_data['ranking_model']
        request_data.stores = serializer.validated_data['stores']
        request_data.products = serializer.validated_data['products']
        request_data.warehouses = serializer.validated_data['warehouses']
        return request_data


class BrandCreationProcessor:
    def execute(self, request):
        data = BrandCreationRequestProcessor().process_post_request_parameters(request)
        brand = self._get_brand(data.name, data.ranking_model)
        self._save_models([brand], BrandModel)
        products = self._get_products(data.products, brand)
        stores = self._get_stores(data.stores, brand)
        warehouses = self._get_warehouses(data.warehouses, brand)
        self._save_models(products, ProductModel)
        self._save_models(stores, StoreModel)
        self._save_models(warehouses, WarehouseModel)

    def _get_brand(self, name, ranking_model):
        brand = BrandModel(name=name, ranking_model=ranking_model)
        return brand

    def _get_products(self, products, brand):
        product_list = list()
        for product in products:
            product_code = product['product_code']
            product_model = ProductModel(product_code=product_code, brand_model=brand)
            product_list.append(product_model)
        return product_list

    def _get_stores(self, stores, brand):
        stores_list = list()
        for store in stores:
            store_code = store['store_code']
            store_model = StoreModel(store_code=store_code, brand_model=brand)
            stores_list.append(store_model)
        return stores_list

    def _get_warehouses(self, warehouses, brand):
        warehouse_list = list()
        for warehouse in warehouses:
            warehouse_code = warehouse['warehouse_code']
            warehouse_model = WarehouseModel(warehouse_code=warehouse_code, brand_model=brand)
            warehouse_list.append(warehouse_model)
        return warehouse_list

    def _save_models(self, models, model_class):
        model_class.objects.bulk_create(models, batch_size=1000)
