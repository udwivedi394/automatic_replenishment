from abc import abstractmethod
from collections import defaultdict
from datetime import timedelta
from typing import Dict

from automatic_replenishment_system.retail_core.core.constants import RankingModel
from automatic_replenishment_system.retail_core.core.utils.csv_utils import CSVInputOutput
from automatic_replenishment_system.retail_core.models import BrandModel, StoreWarehouseMappingModel, \
    StoreInventoryModel, BSQModel, WarehouseInventoryModel, StaticPriorityModel, SalesTransaction


class StoreRankingAttributes:
    def __init__(self, store, quantity, static_rank):
        self.store = store
        self.quantity = quantity
        self.static_rank = static_rank


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
        store_rank_generator = StoreRankFactory.get_store_rank_generator_by_model(self.brand, self.date,
                                                                                  self.brand.ranking_model)
        store_rank_map = store_rank_generator.execute()
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
        date = self.date + timedelta(days=1)
        query = {'brand_model': self.brand, 'date': date}
        warehouse_inventory_rows = ModelExtractor(WarehouseInventoryModel, query,
                                                  prefetch_keys=('warehouse', 'product',)).execute()
        warehouse_product_availibity_map = dict()
        for warehouse_inventory_row in warehouse_inventory_rows:
            filter_key = FilterKey().warehouse_product_key(warehouse_inventory_row.warehouse,
                                                           warehouse_inventory_row.product)
            warehouse_product_availibity_map[filter_key] = warehouse_inventory_row.closing_inventory
        return warehouse_product_availibity_map

    def _store_product_map(self):
        query = {'brand_model': self.brand, 'date': self.date}
        store_inventory_rows = ModelExtractor(StoreInventoryModel, query, prefetch_keys=('store', 'product',)).execute()
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


class ConvertReplenishmentOrder:
    def __init__(self, replenishment_qty_map):
        self.replenishment_qty_map = replenishment_qty_map

    def convert(self):
        replenishement_order_list = list()
        for filter_key, replenishment_qty in self.replenishment_qty_map.items():
            if not replenishment_qty:
                continue
            replenishmement_row = self._gen_replenishment_row(filter_key, replenishment_qty)
            replenishement_order_list.append(replenishmement_row)
        return replenishement_order_list

    def _gen_replenishment_row(self, filter_key, replenishment_qty):
        warehouse, store, product = filter_key
        row = {
            'From Warehouse id': warehouse,
            'To Store id': store,
            'Product/SKU': product,
            'Replenishment Qty': replenishment_qty
        }
        return row


class ConvertShortQtyOrder:
    def __init__(self, short_qty_map):
        self.short_qty_map = short_qty_map

    def convert(self):
        short_qty_row_list = list()
        for filter_key, short_qty in self.short_qty_map.items():
            if not short_qty:
                continue
            short_qty_row = self._gen_short_qty_row(filter_key, short_qty)
            short_qty_row_list.append(short_qty_row)
        return short_qty_row_list

    def _gen_short_qty_row(self, filter_key, short_qty):
        warehouse, product = filter_key
        row = {
            'Warehouse id': warehouse,
            'Product/SKU': product,
            'Short Qty': short_qty
        }
        return row


class GenReplenishment:
    def __init__(self, brand: BrandModel, date):
        self.brand = brand
        self.date = date
        self.map_keeper = StaticMapGenerator(brand=self.brand, date=self.date)

    def execute(self):
        required_qty_map = self._get_required_qty_map()
        overall_product_required_qty_map = self._get_overall_product_required_qty_map(required_qty_map)
        short_qty_map = self._get_short_qty_map(overall_product_required_qty_map)
        replenishment_qty_map = self._get_replenishment_map(required_qty_map)
        replenishment_rows = ConvertReplenishmentOrder(replenishment_qty_map).convert()
        file_name = 'output_data/replenishment_order_{}_{}.csv'.format(self.brand.name, self.date)
        self._write_to_file(replenishment_rows, file_name)
        short_qty_rows = ConvertShortQtyOrder(short_qty_map).convert()
        file_name = 'output_data/short_qty_{}_{}.csv'.format(self.brand.name, self.date)
        self._write_to_file(short_qty_rows, file_name)
        return replenishment_rows

    def _get_required_qty_map(self):
        required_qty_map = dict()
        bsq_models = self._get_bsq_models()
        for bsq_model in bsq_models:
            store, product = bsq_model.store, bsq_model.product
            warehouse = self.map_keeper.store_warehouse_map[bsq_model.store]
            filter_key = FilterKey().warehouse_store_product_key(warehouse, store, product)
            # TODO if store, product combination not available in store_inventory consider it 0
            current_stock_qty = self.map_keeper.store_inventory_map.get(filter_key, 0)
            required_qty = max(0, bsq_model.bsq - current_stock_qty)
            required_qty_map[filter_key] = required_qty
        return required_qty_map

    def _get_bsq_models(self):
        query = {'brand_model': self.brand}
        models = ModelExtractor(BSQModel, query, prefetch_keys=('store', 'product')).execute()
        return models

    def _get_replenishment_map(self, required_qty_map):
        replenish_qty_map = dict()
        total_stores = len(self.map_keeper.store_rank_map)
        for rank in range(1, total_stores + 1):
            store = self.map_keeper.store_rank_map[rank]
            for product in self.map_keeper.store_product_map[store]:
                replenish_qty = self._get_replenish_qty(product, store, required_qty_map)
                warehouse = self.map_keeper.store_warehouse_map[store]
                filter_key = FilterKey().warehouse_store_product_key(warehouse, store, product)
                replenish_qty_map[filter_key] = replenish_qty
                self._reduce_quantity_in_warehouse(warehouse, product, replenish_qty)
        return replenish_qty_map

    def _get_replenish_qty(self, product, store, required_qty_map):
        warehouse = self.map_keeper.store_warehouse_map[store]
        filter_key = FilterKey().warehouse_store_product_key(warehouse, store, product)
        # TODO current product for given store is not maintained in store inventory?
        current_store_required_quantity = required_qty_map.get(filter_key, 0)
        warehouse_product_filter_key = FilterKey().warehouse_product_key(warehouse, product)
        # TODO current product not available in warehouse?
        available_qty_in_warehouse = self.map_keeper.warehouse_prod_avail_qty_map.get(warehouse_product_filter_key, 0)
        replenish_qty = min(available_qty_in_warehouse, current_store_required_quantity)
        return replenish_qty

    def _get_short_qty_map(self, overall_product_required_qty):
        short_qty_map = dict()
        for filter, required_qty in overall_product_required_qty.items():
            available_qty = self.map_keeper.warehouse_prod_avail_qty_map[filter]
            if available_qty >= required_qty:
                continue
            short_qty_map[filter] = required_qty - available_qty
        return short_qty_map

    def _get_overall_product_required_qty_map(self, required_qty_map):
        overall_product_required_qty_map = defaultdict(int)
        for filter_key, required_qty in required_qty_map.items():
            warehouse_code, store_code, product_code = filter_key
            warehouse_product_key = (warehouse_code, product_code)
            overall_product_required_qty_map[warehouse_product_key] += required_qty
        return overall_product_required_qty_map

    def _write_to_file(self, csv_rows, file_name):
        if not csv_rows:
            return
        header = list(csv_rows[0].keys())
        CSVInputOutput().write_csv_to_file_dictwriter(file_name, header, csv_rows)

    def _reduce_quantity_in_warehouse(self, warehouse, product, replenish_qty):
        if not replenish_qty:
            return
        warehouse_product_filter_key = FilterKey().warehouse_product_key(warehouse, product)
        self.map_keeper.warehouse_prod_avail_qty_map[warehouse_product_filter_key] -= replenish_qty


class FilterKey:
    def warehouse_store_product_key(self, warehouse, store, product):
        key = (warehouse.warehouse_code, store.store_code, product.product_code)
        return key

    def warehouse_product_key(self, warehouse, product):
        key = (warehouse.warehouse_code, product.product_code)
        return key


class StoreRankGenerator:
    def __init__(self, brand: BrandModel, date):
        self.brand = brand
        self.date = date

    @abstractmethod
    def execute(self):
        pass


class StaticRankGenerator(StoreRankGenerator):
    def execute(self):
        store_rank_map = dict()
        query = {'brand_model': self.brand}
        static_rank_models = ModelExtractor(StaticPriorityModel, query, prefetch_keys=('store',)).execute()
        for static_rank_model in static_rank_models:
            store_rank_map[static_rank_model.static_priority_rank] = static_rank_model.store
        return store_rank_map


class DynamicRankGenerator(StoreRankGenerator):
    def execute(self):
        store_sales_map = self._get_store_sales_map()
        static_rank_map = self._get_store_static_rank_map()
        store_rank_map = self._gen_store_dynamic_rank_map(store_sales_map, static_rank_map)
        return store_rank_map

    def _get_store_static_rank_map(self):
        store_rank_map = dict()
        query = {'brand_model': self.brand}
        static_rank_models = ModelExtractor(StaticPriorityModel, query, prefetch_keys=('store',)).execute()
        for static_rank_model in static_rank_models:
            store_rank_map[static_rank_model.store] = static_rank_model.static_priority_rank
        return store_rank_map

    def _get_store_sales_map(self):
        start_date = self.date - timedelta(days=7)
        query = {'brand_model': self.brand, 'date__range': (start_date, self.date)}
        sales_transactions = ModelExtractor(SalesTransaction, query=query, prefetch_keys=('store', )).execute()
        store_sales_map = defaultdict(int)
        for sales_transaction in sales_transactions:
            store_sales_map[sales_transaction.store] += sales_transaction.quantity
        return store_sales_map

    def _gen_store_dynamic_rank_map(self, store_sales_map, static_rank_map):
        store_list = self._get_store_attributes_list(store_sales_map, static_rank_map)
        sorted_store_list = self._sort_the_store_list(store_list)
        store_dynamic_rank_map = self._get_store_dynamic_rank_map(sorted_store_list)
        return store_dynamic_rank_map

    def _get_store_attributes_list(self, store_sales_map, static_rank_map):
        store_attributes_list = list()
        for store, quantity in store_sales_map.items():
            static_rank = static_rank_map.get(store)
            store_obj = StoreRankingAttributes(store, quantity, static_rank)
            store_attributes_list.append(store_obj)
        return store_attributes_list

    def _sort_the_store_list(self, store_list):
        sorted_store_list = sorted(store_list, key=lambda x: (x.quantity, x.static_rank))
        return sorted_store_list

    def _get_store_dynamic_rank_map(self, sorted_store_list):
        store_dynamic_rank_map = dict()
        for rank, store_attrib_object in enumerate(sorted_store_list):
            store_dynamic_rank_map[rank + 1] = store_attrib_object.store
        return store_dynamic_rank_map


class StoreRankFactory:
    @staticmethod
    def get_store_rank_generator_by_model(brand, date, ranking_model):
        if ranking_model == RankingModel.STATIC:
            store_rank_generator = StaticRankGenerator
        elif ranking_model == RankingModel.DYNAMIC:
            store_rank_generator = DynamicRankGenerator
        else:
            raise ValueError('Invalid ranking model: {}'.format(ranking_model))
        return store_rank_generator(brand, date)
