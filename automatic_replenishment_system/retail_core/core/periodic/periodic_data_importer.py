from abc import ABC, abstractmethod

from automatic_replenishment_system.retail_core.core.constants import WarehouseConstants
from automatic_replenishment_system.retail_core.core.periodic.replinshment_generator import ModelExtractor
from automatic_replenishment_system.retail_core.core.utils.common import try_timestamp_combinations
from automatic_replenishment_system.retail_core.models import SalesTransaction, StoreModel, ProductModel, BSQModel, \
    StoreInventoryModel, WarehouseModel, WarehouseInventoryModel


class DataImporterFactory:
    @staticmethod
    def get_importer(model):
        if model == 'SalesTransaction':
            importer = SalesTransactionImporter
        elif model == 'BSQModel':
            importer = BSQImporter
        elif model == 'StoreInventoryModel':
            return StoreInventoryImporter
        elif model == 'WarehouseInventoryModel':
            return WarehouseInventoryImporter
        else:
            raise ValueError('No importer exists for model: {}'.format(model))
        return importer


class MapGenerator:
    def get_model_map(self, brand_model, model_class, key):
        model_map = dict()
        query = {'brand_model': brand_model}
        models = ModelExtractor(model_class, query).execute()
        for model in models:
            model_map[getattr(model, key)] = model
        return model_map


# @transaction.atomic()
class BaseImporter(ABC):
    def __init__(self, brand_model, model_class):
        self.brand_model = brand_model
        self.model_class = model_class

    def execute(self, csv_rows):
        models = self.import_data(csv_rows)
        self._save_models(models)

    def import_data(self, csv_rows):
        model_list = list()
        for row in csv_rows:
            transaction_model = self.get_transaction_model(row)
            if transaction_model:
                model_list.append(transaction_model)
        return model_list

    def _save_models(self, models):
        self.model_class.objects.bulk_create(models, batch_size=1000)

    def convert_to_date(self, date):
        probable_dateformats = ['%d/%m/%y']
        converted_date = try_timestamp_combinations(date, probable_dateformats)
        return converted_date

    @abstractmethod
    def get_transaction_model(self, row):
        pass


class SalesTransactionImporter(BaseImporter):
    def __init__(self, brand_model):
        super().__init__(brand_model, SalesTransaction)
        self.store_model_map = MapGenerator().get_model_map(self.brand_model, StoreModel, 'store_code')
        self.product_model_map = MapGenerator().get_model_map(self.brand_model, ProductModel, 'product_code')

    def get_transaction_model(self, row):
        sale_transaction = SalesTransaction()
        sale_transaction.brand_model = self.brand_model
        sale_transaction.store = self.store_model_map[row['Store_Code']]
        product = self.product_model_map.get(row['Product_Code'], None)
        if not product:
            print('Product Code: {} not available'.format(row['Product_Code']))
            return
        sale_transaction.product = self.product_model_map[row['Product_Code']]
        sale_transaction.date = self.convert_to_date(row['Date'])
        sale_transaction.quantity = row['Sales_Qty']
        return sale_transaction


class BSQImporter(BaseImporter):
    def __init__(self, brand_model):
        super().__init__(brand_model, BSQModel)
        self.store_model_map = MapGenerator().get_model_map(self.brand_model, StoreModel, 'store_code')
        self.product_model_map = MapGenerator().get_model_map(self.brand_model, ProductModel, 'product_code')

    def get_transaction_model(self, row):
        bsq_model = BSQModel()
        bsq_model.brand_model = self.brand_model
        bsq_model.store = self.store_model_map[row['Store_Code']]
        bsq_model.product = self.product_model_map[row['Product_Code']]
        bsq_model.bsq = row['BSQ']
        return bsq_model


class StoreInventoryImporter(BaseImporter):
    def __init__(self, brand_model):
        super().__init__(brand_model, StoreInventoryModel)
        self.store_model_map = MapGenerator().get_model_map(self.brand_model, StoreModel, 'store_code')
        self.product_model_map = MapGenerator().get_model_map(self.brand_model, ProductModel, 'product_code')

    def get_transaction_model(self, row):
        store_inventory_model = StoreInventoryModel()
        store_inventory_model.brand_model = self.brand_model
        store_code = self.store_model_map.get(row['Store_Code'])
        if not store_code:
            print('Store Code: {} not available'.format(row['Store_Code']))
            return
        store_inventory_model.store = self.store_model_map[row['Store_Code']]
        store_inventory_model.product = self.product_model_map[row['Product_Code']]
        store_inventory_model.date = self.convert_to_date(row['Date'])
        store_inventory_model.closing_inventory = row['Closing Inventory']
        return store_inventory_model


class WarehouseInventoryImporter(BaseImporter):
    def __init__(self, brand_model):
        super().__init__(brand_model, WarehouseInventoryModel)
        self.warehouse_model_map = MapGenerator().get_model_map(self.brand_model, WarehouseModel, 'warehouse_code')
        self.product_model_map = MapGenerator().get_model_map(self.brand_model, ProductModel, 'product_code')

    def get_transaction_model(self, row):
        warehouse_inventory = WarehouseInventoryModel()
        warehouse_inventory.brand_model = self.brand_model
        warehouse_inventory.warehouse = self.warehouse_model_map[
            row.get('Warehouse_Code', WarehouseConstants.DEFAULT_WAREHOUSE_CODE)]
        product = self.product_model_map.get(row['Product_Code'], None)
        if not product:
            print('Product Code: {} not available'.format(row['Product_Code']))
            return
        warehouse_inventory.product = product
        warehouse_inventory.date = self.convert_to_date(row['Date'])
        warehouse_inventory.closing_inventory = row['WH_Qty']
        return warehouse_inventory
