from automatic_replenishment_system.retail_core.core.periodic.importer_interface import ImporterInterface
from automatic_replenishment_system.retail_core.core.replenishment_order.utils import ModelExtractor
from automatic_replenishment_system.retail_core.models import FileHandler, FileModel, BrandModel


class OrderFilesImporter:
    def __init__(self, brand_id, file_handler_id):
        self.brand_model = self._get_brand_model(brand_id)
        self.file_handler = self._get_file_handler_model(file_handler_id)

    def execute(self):
        file_models = self._get_file_models()
        for file in file_models:
            ImporterInterface(file.file_type, self.brand_model, file=file.file).execute()

    def _get_file_handler_model(self, file_handler_id):
        return FileHandler.objects.get(id=file_handler_id)

    def _get_file_models(self):
        query = {'id__in': self.file_handler.file_list}
        return ModelExtractor(FileModel, query=query).execute()

    def _get_brand_model(self, brand_id):
        brand_model = BrandModel.objects.filter(id=brand_id).first()
        return brand_model
