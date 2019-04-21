from automatic_replenishment_system.retail_core.core.periodic.periodic_data_importer import DataImporterFactory
from automatic_replenishment_system.retail_core.core.utils.csv_utils import FieldFileCsvHelper
from automatic_replenishment_system.retail_core.models import BrandModel


class ImporterInterface:
    def __init__(self, model_name: str, brand: BrandModel, file: str, reader=FieldFileCsvHelper()):
        self.model_name = model_name
        self.brand = brand
        self.file = file
        self.reader = reader

    def execute(self):
        importer_class = DataImporterFactory.get_importer(self.model_name)
        importer = importer_class(brand_model=self.brand)
        csv_rows, _ = self.reader.read_csv_file(self.file)
        importer.execute(csv_rows)
