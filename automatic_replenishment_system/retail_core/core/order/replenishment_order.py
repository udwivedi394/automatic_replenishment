from automatic_replenishment_system.retail_core.models import Order
from automatic_replenishment_system.taskapp.tasks import import_files_to_models


class ReplenishmentManager:
    def __init__(self, brand_model, date, file_handler):
        self.brand_model = brand_model
        self.date = date
        self.file_handler = file_handler

    def execute(self):
        self._import_files_to_models()

    def _import_files_to_models(self):
        order = self._get_order()
        import_files_to_models.delay(self.brand_model.id, self.file_handler.id, order.id)

    def _get_order(self):
        order = Order(brand_model=self.brand_model, date=self.date, ranking_model=self.brand_model.ranking_model)
        order.save()
        return order
