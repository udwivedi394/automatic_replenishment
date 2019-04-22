from celery import shared_task

from automatic_replenishment_system.retail_core.core.replenishment_order.replenishment_generator import GenReplenishment


@shared_task()
def run_replenishment_order(brand_id, date):
    print('Generating Replenishment order for brand_id {} for date {}'.format(brand_id, date))
    GenReplenishment(brand_id, date).execute()
