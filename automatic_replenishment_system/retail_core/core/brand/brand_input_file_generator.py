from automatic_replenishment_system.retail_core.core.constants import WarehouseConstants, \
    BrandFilesConstants
from automatic_replenishment_system.retail_core.core.utils.csv_utils import CSVInputOutput


class BrandInputFileGenerator:
    def __init__(self, store_inventory, bsq, store_priority_static, output_product_list,
                 output_store_list, output_warehouse_list):
        self.store_inventory = store_inventory
        self.bsq = bsq
        self.store_priority_static = store_priority_static
        self.output_product_list = output_product_list
        self.output_store_list = output_store_list
        self.output_warehouse_list = output_warehouse_list

    def execute(self):
        store_inventory_rows, _ = CSVInputOutput().read_csv_file(self.store_inventory)
        bsq_rows, _ = CSVInputOutput().read_csv_file(self.bsq)
        store_priority_static_rows, _ = CSVInputOutput().read_csv_file(self.store_priority_static)
        self._write_product_list(bsq_rows, store_inventory_rows)
        self._write_store_list(store_priority_static_rows)
        self._write_warehouse_list(store_priority_static_rows)

    def _write_product_list(self, bsq_rows, store_inventory_rows):
        product_list = self._gen_product_list(bsq_rows, store_inventory_rows)
        header = [BrandFilesConstants.PRODUCT_CODE]
        CSVInputOutput().write_csv_to_file_dictwriter(self.output_product_list, header, product_list)

    def _write_store_list(self, store_priority_static_rows):
        store_list = self._gen_store_list(store_priority_static_rows)
        header = [BrandFilesConstants.STORE_CODE]
        CSVInputOutput().write_csv_to_file_dictwriter(self.output_store_list, header, store_list)

    def _gen_store_list(self, store_priority_static_rows):
        store_set = set()
        for store_priority_static_row in store_priority_static_rows:
            store_code = store_priority_static_row[BrandFilesConstants.STORE_CODE]
            store_set.add(store_code)
        store_dict_list = self._generate_dict_list(store_set, BrandFilesConstants.STORE_CODE)
        return store_dict_list

    def _gen_warehouse_list(self, store_priority_static_rows):
        warehouse_list = self._gen_store_list(store_priority_static_rows)
        self._add_warehouse_code(warehouse_list)
        return warehouse_list

    def _gen_product_list(self, bsq_rows, store_inventory_rows):
        product_set = set()
        for bsq_row in bsq_rows:
            product_code = bsq_row[BrandFilesConstants.PRODUCT_CODE]
            product_set.add(product_code)
        for store_inventory_row in store_inventory_rows:
            product_code = store_inventory_row[BrandFilesConstants.PRODUCT_CODE]
            product_set.add(product_code)
        product_dict_list = self._generate_dict_list(product_set, BrandFilesConstants.PRODUCT_CODE)
        return product_dict_list

    def _generate_dict_list(self, value_set, header):
        value_dict_list = list()
        for value in value_set:
            value_dict = {header: value}
            value_dict_list.append(value_dict)
        return value_dict_list

    def _write_warehouse_list(self, store_priority_static_rows):
        warehouse_list = self._gen_warehouse_list(store_priority_static_rows)
        header = [BrandFilesConstants.STORE_CODE, BrandFilesConstants.WAREHOUSE_CODE]
        CSVInputOutput().write_csv_to_file_dictwriter(self.output_warehouse_list, header, warehouse_list)

    def _add_warehouse_code(self, store_list):
        for store in store_list:
            store[BrandFilesConstants.WAREHOUSE_CODE] = WarehouseConstants.DEFAULT_WAREHOUSE_CODE
