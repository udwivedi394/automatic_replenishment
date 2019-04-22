from collections import defaultdict
from datetime import timedelta

from automatic_replenishment_system.retail_core.core.replenishment_order.store_rank_generator import StoreRankFactory
from automatic_replenishment_system.retail_core.core.replenishment_order.utils import FilterKey, ModelExtractor
from automatic_replenishment_system.retail_core.models import BrandModel, StoreWarehouseMappingModel, \
    StoreInventoryModel, WarehouseInventoryModel


class StaticMapGenerator:
    def __init__(self, brand: BrandModel, date):
        self.brand = brand
        self.date = date
        self.store_rank_map = self._get_store_rank_map()
        self.store_warehouse_map = self._get_store_warehouse_map()
        self.store_inventory_map = self._get_inventory_map()
        self.store_product_map = self._store_product_map()
        self.warehouse_prod_avail_qty_map = self._get_warehouse_product_availability_map()

    def _get_store_rank_map(self):
        store_rank_generator = StoreRankFactory.get_store_rank_generator_by_model(self.brand, self.date,
                                                                                  self.brand.ranking_model)
        store_rank_map = store_rank_generator.execute()
        return store_rank_map

    def _get_store_warehouse_map(self):
        query = {'store__brand_model': self.brand}
        store_warehouse_models = ModelExtractor(StoreWarehouseMappingModel, query=query,
                                                prefetch_keys=('store', 'warehouse',)).execute()
        store_warehouse_map = dict()
        for store_warehouse_model in store_warehouse_models:
            store_warehouse_map[store_warehouse_model.store] = store_warehouse_model.warehouse
        return store_warehouse_map

    def _get_inventory_map(self):
        query = {'brand_model': self.brand, 'date': self.date}
        store_inventory_models = ModelExtractor(StoreInventoryModel, query=query,
                                                prefetch_keys=('store', 'product',)).execute()
        store_inventory_map = dict()
        for store_inventory_model in store_inventory_models:
            store, product = store_inventory_model.store, store_inventory_model.product
            warehouse = self.store_warehouse_map[store_inventory_model.store]
            filter_key = FilterKey().warehouse_store_product_key(warehouse, store, product)
            store_inventory_map[filter_key] = store_inventory_model.closing_inventory
        return store_inventory_map

    def _get_warehouse_product_availability_map(self):
        date = self.date + timedelta(days=1)
        query = {'brand_model': self.brand, 'date': date}
        warehouse_inventory_rows = ModelExtractor(WarehouseInventoryModel, query,
                                                  prefetch_keys=('warehouse', 'product',)).execute()
        warehouse_product_availability_map = dict()
        for warehouse_inventory_row in warehouse_inventory_rows:
            filter_key = FilterKey().warehouse_product_key(warehouse_inventory_row.warehouse,
                                                           warehouse_inventory_row.product)
            warehouse_product_availability_map[filter_key] = warehouse_inventory_row.closing_inventory
        print(warehouse_product_availability_map)
        return warehouse_product_availability_map

    def _store_product_map(self):
        query = {'brand_model': self.brand, 'date': self.date}
        store_inventory_rows = ModelExtractor(StoreInventoryModel, query, prefetch_keys=('store', 'product',)).execute()
        store_product_map = defaultdict(list)
        for store_inventory_row in store_inventory_rows:
            store_product_map[store_inventory_row.store].append(store_inventory_row.product)
        return store_product_map
