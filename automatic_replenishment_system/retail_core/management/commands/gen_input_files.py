"""
Helps to generate one-time input files from periodic data
    Example usage: docker-compose -f local.yml run --rm django python manage.py gen_input_files --store_inventory input_data/Store_Inventory-1.csv --bsq input_data/bsq-1.csv --store_priority_static input_data/stores_priority_static.csv --product_list input_data/one_time_data/product_list.csv --store_list input_data/one_time_data/store_list.csv --warehouse_list input_data/one_time_data/warehouse_list.csv
"""

from django.core.management import BaseCommand

from automatic_replenishment_system.retail_core.core.brand.brand_input_file_generator import BrandInputFileGenerator


class Command(BaseCommand):
    help = "Populate Drivers model"

    def add_arguments(self, parser):
        # TODO specify the type of inputs(input/output)
        parser.add_argument('--store_inventory', type=str, help='Input Path to store_inventory file')
        parser.add_argument('--bsq', type=str, help="Input Path to bsq file")
        parser.add_argument('--store_priority_static', type=str, help="Input Path to store_priority_static file")
        parser.add_argument('--product_list', type=str, help='Output--> path to export product list ')
        parser.add_argument('--store_list', type=str, help='Output--> path to export store list')
        parser.add_argument('--warehouse_list', type=str, help='Output--> path to export warehouse list')

    def handle(self, *args, **kwargs):
        store_inventory = kwargs['store_inventory']
        bsq = kwargs['bsq']
        store_priority_static = kwargs['store_priority_static']
        output_product_list = kwargs['product_list']
        output_store_list = kwargs['store_list']
        output_warehouse_list = kwargs['warehouse_list']
        BrandInputFileGenerator(store_inventory, bsq, store_priority_static, output_product_list, output_store_list,
                                output_warehouse_list).execute()
