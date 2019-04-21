from django.urls import reverse

from automatic_replenishment_system.retail_core.core.utils.csv_utils import FieldFileCsvHelper
from automatic_replenishment_system.retail_core.core.utils.request_maker import RequestMaker


class BrandCreationProcessManager:
    def __init__(self, brand, product_file, store_file, warehouse_file, static_rank_file):
        self.brand = brand
        self.product_file = product_file
        self.store_file = store_file
        self.warehouse_file = warehouse_file
        self.static_rank_file = static_rank_file
        self.brand_importer_api = 'http://0.0.0.0:8000' + reverse('brand_importer')

    def execute(self):
        products, _ = FieldFileCsvHelper().read_csv_file(self.product_file)
        stores, _ = FieldFileCsvHelper().read_csv_file(self.store_file)
        warehouses, _ = FieldFileCsvHelper().read_csv_file(self.warehouse_file)
        static_ranks, _ = FieldFileCsvHelper().read_csv_file(self.static_rank_file)
        post_data = self._get_post_parameters(products, stores, warehouses, static_ranks)
        self._call_api(post_data)

    def _get_post_parameters(self, products, stores, warehouses, static_ranks):
        post_data = dict()
        post_data['name'] = self.brand.name
        post_data['ranking_model'] = self.brand.ranking_model
        post_data['stores'] = stores
        post_data['products'] = products
        post_data['warehouses'] = warehouses
        post_data['static_ranks'] = static_ranks
        return post_data

    def _call_api(self, request_parameters):
        response = RequestMaker().post_request(self.brand_importer_api, request_parameters, retry=3)
        return response
