from automatic_replenishment_system.retail_core.models import FileModel, FileHandler


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
