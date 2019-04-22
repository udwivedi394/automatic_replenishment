from automatic_replenishment_system.retail_core.core.periodic.importer_interface import ImporterInterface
from automatic_replenishment_system.retail_core.core.periodic.replinshment_generator import GenReplenishment
from automatic_replenishment_system.retail_core.models import BSQModel, SalesTransaction, StoreInventoryModel, \
    WarehouseInventoryModel


class ReplenishmentManager:
    def __init__(self, brand_model, date, bsq_file, sales_transactions_file, store_inventory_file,
                 warehouse_inventory_file):
        self.brand_model = brand_model
        self.date = date
        self.bsq_file = bsq_file
        self.sales_transactions_file = sales_transactions_file
        self.store_inventory_file = store_inventory_file
        self.warehouse_inventory_file = warehouse_inventory_file

    def execute(self):
        self._import_files_to_models()
        self._generate_replenishment_order()

    def _import_files_to_models(self):
        ImporterInterface(BSQModel.__name__, self.brand_model, file=self.bsq_file).execute()
        ImporterInterface(SalesTransaction.__name__, self.brand_model, file=self.sales_transactions_file).execute()
        ImporterInterface(StoreInventoryModel.__name__, self.brand_model, file=self.store_inventory_file).execute()
        ImporterInterface(WarehouseInventoryModel.__name__, self.brand_model,
                          file=self.warehouse_inventory_file).execute()

    def _generate_replenishment_order(self):
        GenReplenishment(self.brand_model, self.date).execute()
