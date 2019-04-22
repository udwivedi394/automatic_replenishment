import datetime

from automatic_replenishment_system.retail_core.models import Order, FileModel, FileHandler
from automatic_replenishment_system.taskapp.tasks import run_replenishment_order, import_files_to_models


class FileModelGenerator:
    def __init__(self, bsq_file, sales_transactions_file, store_inventory_file,
                 warehouse_inventory_file):
        self.bsq_file = bsq_file
        self.sales_transactions_file = sales_transactions_file
        self.store_inventory_file = store_inventory_file
        self.warehouse_inventory_file = warehouse_inventory_file

    def execute(self):
        files = self._get_all_file_models()
        self._save_models(files)
        file_handler = self._get_file_handler(files)
        return file_handler

    def _get_all_file_models(self):
        bsq_file = FileModel()
        bsq_file.file_type = 'BSQModel'
        bsq_file.file = self.bsq_file

        sales_transaction = FileModel()
        sales_transaction.file_type = 'SalesTransaction'
        sales_transaction.file = self.sales_transactions_file

        store_inventory = FileModel()
        store_inventory.file_type = 'StoreInventoryModel'
        store_inventory.file = self.store_inventory_file

        warehouse_inventory = FileModel()
        warehouse_inventory.file_type = 'WarehouseInventoryModel'
        warehouse_inventory.file = self.warehouse_inventory_file
        return [bsq_file, sales_transaction, store_inventory, warehouse_inventory]

    def _save_models(self, files):
        FileModel.objects.bulk_create(files, batch_size=10)

    def _get_file_handler(self, files):
        file_handler = FileHandler()
        file_handler.file_list = [file.id for file in files]
        file_handler.save()
        return file_handler


class ReplenishmentManager:
    def __init__(self, brand_model, date, file_handler):
        self.brand_model = brand_model
        self.date = date
        self.file_handler = file_handler

    def execute(self):
        self._import_files_to_models()
        # self._generate_replenishment_order()

    def _import_files_to_models(self):
        order = self._get_order()
        import_files_to_models.delay(self.brand_model.id, self.file_handler.id, order.id)
        # ImporterInterface(BSQModel.__name__, self.brand_model, file=self.bsq_file).execute()
        # ImporterInterface(SalesTransaction.__name__, self.brand_model, file=self.sales_transactions_file).execute()
        # ImporterInterface(StoreInventoryModel.__name__, self.brand_model, file=self.store_inventory_file).execute()
        # ImporterInterface(WarehouseInventoryModel.__name__, self.brand_model,
        #                   file=self.warehouse_inventory_file).execute()

    def _generate_replenishment_order(self):
        order = self._get_order()
        # date_string = self._convert_to_proper_format(self.date)
        run_replenishment_order.delay(order.id)

    def _convert_to_proper_format(self, date):
        converted_date = datetime.datetime.strftime(date, '%Y-%m-%d')
        print(converted_date)
        return converted_date

    def _get_order(self):
        order = Order(brand_model=self.brand_model, date=self.date, ranking_model=self.brand_model.ranking_model)
        order.save()
        return order
