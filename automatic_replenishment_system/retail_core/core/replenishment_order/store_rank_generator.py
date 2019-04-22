from abc import abstractmethod
from collections import defaultdict
from datetime import timedelta

from automatic_replenishment_system.retail_core.core.constants import RankingModel
from automatic_replenishment_system.retail_core.core.replenishment_order.utils import ModelExtractor
from automatic_replenishment_system.retail_core.models import BrandModel, StaticPriorityModel, SalesTransaction


class StoreRankingAttributes:
    def __init__(self, store, quantity, static_rank):
        self.store = store
        self.quantity = quantity
        self.static_rank = static_rank


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
        sales_transactions = ModelExtractor(SalesTransaction, query=query, prefetch_keys=('store',)).execute()
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
