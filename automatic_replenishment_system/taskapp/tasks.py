from celery import shared_task

from automatic_replenishment_system.retail_core.core.periodic.file_importer import OrderFilesImporter
from automatic_replenishment_system.retail_core.core.replenishment_order.replenishment_generator import GenReplenishment
from automatic_replenishment_system.retail_core.models import Order


@shared_task()
def run_replenishment_order(order_id):
    order = Order.objects.get(id=order_id)
    print('Generating Replenishment order for brand_id {} for date {}'.format(order.brand_model.id, order.date))
    GenReplenishment(order.brand_model.id, order.date).execute()
    order.completed = True
    order.save()


@shared_task()
def import_files_to_models(brand_id, file_handler_id, order_id):
    print('Importing files for brand_id {}'.format(brand_id))
    OrderFilesImporter(brand_id, file_handler_id).execute()
    run_replenishment_order.delay(order_id)
