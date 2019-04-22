from collections import defaultdict
from typing import Dict

from automatic_replenishment_system.retail_core.core.replenishment_order.map_generator import StaticMapGenerator
from automatic_replenishment_system.retail_core.core.replenishment_order.utils import ModelExtractor, FilterKey, \
    MapGenerator
from automatic_replenishment_system.retail_core.core.utils.csv_utils import CSVInputOutput
from automatic_replenishment_system.retail_core.models import BrandModel, BSQModel, ReplenishmentOrderModel, \
    WarehouseProductShortQtyModel, StoreModel, ProductModel, WarehouseModel


class OrderBaseAttributes:
    def __init__(self, brand: BrandModel, date, ranking_model: str):
        self.brand = brand
        self.date = date
        self.ranking_model = ranking_model


class CodeModelMapper:
    def __init__(self, brand_model):
        self.store_model_map = MapGenerator().get_model_map(brand_model, StoreModel, 'store_code')
        self.product_model_map = MapGenerator().get_model_map(brand_model, ProductModel, 'product_code')
        self.warehouse_model_map = MapGenerator().get_model_map(brand_model, WarehouseModel, 'warehouse_code')


class ConvertReplenishmentOrder:
    def __init__(self, replenishment_qty_map: Dict, order_base: OrderBaseAttributes):
        self.replenishment_qty_map = replenishment_qty_map
        self.order_base = order_base
        self.code_mapper = CodeModelMapper(self.order_base.brand)

    def convert(self):
        replenishment_order_list = list()
        for filter_key, replenishment_qty in self.replenishment_qty_map.items():
            if not replenishment_qty:
                continue
            replenishment_row = self._gen_replenishment_model(filter_key, replenishment_qty)
            replenishment_order_list.append(replenishment_row)
        return replenishment_order_list

    def _gen_replenishment_model(self, filter_key, replenishment_qty):
        warehouse_code, store_code, product_code = filter_key
        replenishment_model = ReplenishmentOrderModel()
        replenishment_model.brand_model = self.order_base.brand
        replenishment_model.ranking_model = self.order_base.ranking_model
        replenishment_model.date = self.order_base.date
        replenishment_model.warehouse = self.code_mapper.warehouse_model_map[warehouse_code]
        replenishment_model.store = self.code_mapper.store_model_map[store_code]
        replenishment_model.product = self.code_mapper.product_model_map[product_code]
        replenishment_model.replenishment_qty = replenishment_qty
        return replenishment_model


class ConvertShortQtyOrder:
    def __init__(self, short_qty_map: Dict, order_base: OrderBaseAttributes):
        self.short_qty_map = short_qty_map
        self.order_base = order_base
        self.code_mapper = CodeModelMapper(self.order_base.brand)

    def convert(self):
        short_qty_model_list = list()
        for filter_key, short_qty in self.short_qty_map.items():
            if not short_qty:
                continue
            short_qty_model = self._gen_short_qty_row(filter_key, short_qty)
            short_qty_model_list.append(short_qty_model)
        return short_qty_model_list

    def _gen_short_qty_row(self, filter_key, short_qty):
        warehouse_code, product_code = filter_key
        short_qty_model = WarehouseProductShortQtyModel()
        short_qty_model.brand_model = self.order_base.brand
        short_qty_model.ranking_model = self.order_base.ranking_model
        short_qty_model.date = self.order_base.date
        short_qty_model.warehouse = self.code_mapper.warehouse_model_map[warehouse_code]
        short_qty_model.product = self.code_mapper.product_model_map[product_code]
        short_qty_model.short_qty = short_qty
        return short_qty_model


class GenReplenishment:
    def __init__(self, brand: BrandModel, date):
        self.brand = brand
        self.date = date
        self.map_keeper = StaticMapGenerator(brand=self.brand, date=self.date)
        self.order_attributes = self._get_order_attributes()

    def execute(self):
        required_qty_map = self._get_required_qty_map()
        overall_product_required_qty_map = self._get_overall_product_required_qty_map(required_qty_map)
        short_qty_map = self._get_short_qty_map(overall_product_required_qty_map)
        replenishment_qty_map = self._get_replenishment_map(required_qty_map)
        replenishment_models = self._get_replenishment_models(replenishment_qty_map)
        short_qty_models = self._get_short_qty_models(short_qty_map)
        self._save_models(ReplenishmentOrderModel, replenishment_models)
        self._save_models(WarehouseProductShortQtyModel, short_qty_models)
        return True

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

    def _get_replenishment_models(self, replenishment_qty_map):
        replenishment_models = ConvertReplenishmentOrder(replenishment_qty_map,
                                                         order_base=self.order_attributes).convert()
        return replenishment_models

    def _get_short_qty_models(self, short_qty_map):
        short_qty_models = ConvertShortQtyOrder(short_qty_map, order_base=self.order_attributes).convert()
        return short_qty_models

    def _get_order_attributes(self):
        order_attributes = OrderBaseAttributes(brand=self.brand, date=self.date, ranking_model=self.brand.ranking_model)
        return order_attributes

    def _save_models(self, model_class, models):
        model_class.objects.bulk_create(models)
