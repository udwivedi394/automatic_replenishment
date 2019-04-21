from abc import abstractmethod
from collections import defaultdict
from typing import Dict

from automatic_replenishment_system.retail_core.core.constants import RankingModel
from automatic_replenishment_system.retail_core.models import BrandModel, StoreWarehouseMappingModel, \
    StoreInventoryModel, BSQModel, WarehouseInventoryModel, StaticPriorityModel


class StaticMapGenerator:
    def __init__(self, brand: BrandModel, date):
        self.brand = brand
        self.date = date
        self.store_rank_map = self._get_store_rank_map()
        self.store_warehouse_map = self._get_store_warehouse_map()
        self.store_inventory_map = self._get_inventory_map()
        self.store_product_map = self._store_product_map()
        self.warehouse_prod_avail_qty_map = self._get_warehouse_product_availibity_map()

    def _get_store_rank_map(self):
        store_rank_map = StoreRankFactory.get_store_rank_generator_by_model(self.brand,
                                                                            self.brand.ranking_model).execute()
        return store_rank_map

    def _get_store_warehouse_map(self):
        store_warehouse_models = StoreWarehouseMappingModel.objects.filter(
            store__brand_model=self.brand).prefetch_related('store', 'warehouse')
        store_warehouse_map = dict()
        for store_warehouse_model in store_warehouse_models:
            store_warehouse_map[store_warehouse_model.store] = store_warehouse_model.warehouse
        return store_warehouse_map

    def _get_inventory_map(self):
        store_inventory_models = StoreInventoryModel.objects.filter(brand_model=self.brand,
                                                                    date=self.date).prefetch_related('store', 'product')
        store_inventory_map = dict()
        for store_inventory_model in store_inventory_models:
            store, product = store_inventory_model.store, store_inventory_model.product
            warehouse = self.store_warehouse_map[store_inventory_model.store]
            filter_key = FilterKey().warehouse_store_product_key(warehouse, store, product)
            store_inventory_map[filter_key] = store_inventory_model.closing_inventory
        return store_inventory_map

    def _get_warehouse_product_availibity_map(self):
        query = {'brand_model': self.brand, 'date': self.date}
        warehouse_inventory_rows = ModelExtractor(WarehouseInventoryModel, query,
                                                  prefetch_keys=('warehouse', 'product')).execute()
        warehouse_product_availibity_map = dict()
        for warehouse_inventory_row in warehouse_inventory_rows:
            filter_key = FilterKey().warehouse_product_key(warehouse_inventory_row.warehouse,
                                                           warehouse_inventory_row.warehouse.product)
            warehouse_product_availibity_map[filter_key] = warehouse_inventory_row.closing_inventory
        return warehouse_product_availibity_map

    def _store_product_map(self):
        query = {'brand_model': self.brand, 'date': self.date}
        store_inventory_rows = ModelExtractor(StoreInventoryModel, query, prefetch_keys=('store', 'product')).execute()
        store_product_map = defaultdict(list)
        for store_inventory_row in store_inventory_rows:
            store_product_map[store_inventory_row.store].append(store_inventory_row.product)
        return store_product_map


class ModelExtractor:
    def __init__(self, model_class, query: Dict, prefetch_keys=()):
        self.model_class = model_class
        self.query = query
        self.prefetch_keys = prefetch_keys

    def execute(self):
        models = self.model_class.objects.filter(**self.query).prefetch_related(*self.prefetch_keys)
        return models


class GenReplenishment:
    def __init__(self, brand: BrandModel, date):
        self.brand = brand
        self.date = date
        self.map_keeper = StaticMapGenerator(brand=self.brand, date=self.date)

    def execute(self):
        required_qty_map = self._get_required_qty_map()
        overall_product_required_qty_map = self._get_overall_product_required_qty_map(required_qty_map)
        replenishment_qty_map = self._get_replenishment_map(required_qty_map, overall_product_required_qty_map)
        short_qty_map = self._get_short_qty_map(required_qty_map)
        print(replenishment_qty_map)
        print(short_qty_map)

    def _get_required_qty_map(self):
        required_qty_map = dict()
        bsq_models = self._get_bsq_models()
        for bsq_model in bsq_models:
            store, product = bsq_model.store, bsq_model.product
            warehouse = self.map_keeper.store_warehouse_map[bsq_model.store]
            filter_key = FilterKey().warehouse_store_product_key(warehouse, store, product)
            current_stock_qty = self.map_keeper.store_inventory_map[filter_key]
            required_qty = max(0, bsq_model.bsq - current_stock_qty)
            required_qty_map[filter_key] = required_qty
        return required_qty_map

    def _get_bsq_models(self):
        query = {'brand_model': self.brand}
        models = ModelExtractor(BSQModel, query, prefetch_keys=('store', 'product')).execute()
        return models

    def _get_replenishment_map(self, required_qty_map, overall_product_required_qty_map):
        replenish_qty_map = dict()
        total_stores = len(self.map_keeper.store_rank_map)
        for rank in range(1, total_stores + 1):
            store = self.map_keeper.store_rank_map[rank]
            for product in self.map_keeper.store_product_map[store]:
                replenish_qty = self._get_replenish_qty(product, store, required_qty_map,
                                                        overall_product_required_qty_map)
                warehouse = self.map_keeper.store_warehouse_map[store]
                filter_key = FilterKey().warehouse_store_product_key(warehouse, store, product)
                replenish_qty_map[filter_key] = replenish_qty
        return replenish_qty_map

    def _get_replenish_qty(self, product, store, required_qty_map, overall_product_required_qty_map):
        warehouse = self.map_keeper.store_warehouse_map[store]
        filter_key = FilterKey().warehouse_store_product_key(warehouse, store, product)
        current_store_required_quantity = required_qty_map[filter_key]
        warehouse_product_filter_key = FilterKey().warehouse_product_key(warehouse, product)
        available_quantity_in_warehouse = self.map_keeper.warehouse_prod_avail_qty_map[
            warehouse_product_filter_key]
        # across_stores_required_qty = self.map_keeper.overall_product_required_qty_map[
        #     warehouse_product_filter_key]
        replenish_qty = min(available_quantity_in_warehouse, current_store_required_quantity)
        return replenish_qty

    def _get_short_qty_map(self, required_qty_map):
        pass

    def _get_overall_product_required_qty_map(self, required_qty_map):
        overall_product_required_qty_map = defaultdict(int)
        for filter_key, required_qty in required_qty_map.items():
            warehouse_code, store_code, product_code = filter_key
            warehouse_product_key = (warehouse_code, product_code)
            overall_product_required_qty_map[warehouse_product_key] += required_qty
        return overall_product_required_qty_map


class FilterKey:
    def warehouse_store_product_key(self, warehouse, store, product):
        key = (warehouse.warehouse_code, store.store_code, product.product_code)
        return key

    def warehouse_product_key(self, warehouse, product):
        key = (warehouse.warehouse_code, product.product_code)
        return key


class StoreRankGenerator:
    def __init__(self, brand: BrandModel):
        self.brand = brand

    @abstractmethod
    def execute(self):
        pass


class StaticRankGenerator(StoreRankGenerator):
    def execute(self):
        store_rank_map = dict()
        query = {'brand_model': self.brand}
        static_rank_models = ModelExtractor(StaticPriorityModel, query, prefetch_keys=('store')).execute()
        for static_rank_model in static_rank_models:
            store_rank_map[static_rank_model.static_priority_rank] = static_rank_model.store
        return store_rank_map


class DynamicRankGenerator(StoreRankGenerator):
    def execute(self):
        pass


class StoreRankFactory:
    @staticmethod
    def get_store_rank_generator_by_model(brand, ranking_model):
        if ranking_model == RankingModel.STATIC:
            store_rank_generator = StaticRankGenerator(brand)
        elif ranking_model == RankingModel.DYNAMIC:
            store_rank_generator = DynamicRankGenerator(brand)
        else:
            raise ValueError('Invalid ranking model: {}'.format(ranking_model))
        return store_rank_generator
