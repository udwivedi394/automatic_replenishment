from typing import Dict


class ModelExtractor:
    def __init__(self, model_class, query: Dict, prefetch_keys=()):
        self.model_class = model_class
        self.query = query
        self.prefetch_keys = prefetch_keys

    def execute(self):
        models = self.model_class.objects.filter(**self.query).prefetch_related(*self.prefetch_keys)
        return models


class FilterKey:
    def warehouse_store_product_key(self, warehouse, store, product):
        key = (warehouse.warehouse_code, store.store_code, product.product_code)
        return key

    def warehouse_product_key(self, warehouse, product):
        key = (warehouse.warehouse_code, product.product_code)
        return key


class ModelConverter:
    @staticmethod
    def convert_to_replenishment_order_rows(replenishment_models):
        replenishment_rows = list()
        for replenishment_model in replenishment_models:
            row = {
                'From Warehouse id': replenishment_model.warehouse.warehouse_code,
                'To Store id': replenishment_model.store.store_code,
                'Product/SKU': replenishment_model.product.product_code,
                'Replenishment Qty': replenishment_model.replenishment_qty
            }
            replenishment_rows.append(row)
        return replenishment_rows

    @staticmethod
    def convert_to_short_quantity_order_rows(short_qty_models):
        short_qty_rows = list()
        for short_qty_model in short_qty_models:
            row = {
                'Warehouse id': short_qty_model.warehouse.warehouse_code,
                'Product/SKU': short_qty_model.product.product_code,
                'Short Qty': short_qty_model.short_qty
            }
            short_qty_rows.append(row)
        return short_qty_rows


class MapGenerator:
    def get_model_map(self, brand_model, model_class, key):
        model_map = dict()
        query = {'brand_model': brand_model}
        models = ModelExtractor(model_class, query).execute()
        for model in models:
            model_map[getattr(model, key)] = model
        return model_map
