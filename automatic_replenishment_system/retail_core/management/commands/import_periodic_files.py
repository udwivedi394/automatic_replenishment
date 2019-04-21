"""
Helps to populate CSV files to Models
    Example usage: docker-compose -f local.yml run --rm django python manage.py import_periodic_files --brand Testing_1 --model SalesTransaction --csvfile input_data/Sales-1.csv
"""

from django.core.management import BaseCommand

from automatic_replenishment_system.retail_core.core.periodic.importer_interface import ImporterInterface
from automatic_replenishment_system.retail_core.core.utils.csv_utils import CSVInputOutput
from automatic_replenishment_system.retail_core.models import BrandModel


class Command(BaseCommand):
    help = 'Upload CSV to Models'

    def add_arguments(self, parser):
        parser.add_argument('--brand', type=str, help="Brand Name")
        parser.add_argument('--model', type=str, help='Model to be populated')
        parser.add_argument('--csvfile', type=str, help="CSV file to be uploaded")

    def handle(self, *args, **kwargs):
        brand = kwargs['brand']
        model = kwargs['model']
        csvfile = kwargs['csvfile']
        brand_model = BrandModel.objects.get(name=brand)
        ImporterInterface(model_name=model, brand=brand_model, file=csvfile, reader=CSVInputOutput()).execute()
