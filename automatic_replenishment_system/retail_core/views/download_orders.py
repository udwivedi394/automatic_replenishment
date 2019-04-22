from abc import abstractmethod

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views import View

from automatic_replenishment_system.retail_core.core.replenishment_order.utils import ModelExtractor, ModelConverter
from automatic_replenishment_system.retail_core.core.utils.csv_utils import ExportAsCsv
from automatic_replenishment_system.retail_core.models import BrandModel, Order, ReplenishmentOrderModel, \
    WarehouseProductShortQtyModel


class OrderDownloadResponse:
    def __init__(self, request):
        self.request = request

    def execute(self):
        report_type, order_id = self._get_order_id(self.request.POST)
        downloader = ReportDownloadFactory.get_downloader(report_type)
        response = downloader(order_id).execute()
        return response

    def _get_order_id(self, POST):
        download_data = POST['download_order']
        report_type, order_id = download_data.split('-')
        return report_type, order_id


class Downloader:
    def __init__(self, order_id):
        self.order = self._get_order(order_id)
        self.model_class = self.get_model_class()
        self.extra_keys = self.get_prefetch_keys()

    def _get_order(self, order_id):
        order = Order.objects.get(id=order_id)
        return order

    def execute(self):
        csv_rows, header = self.get_csv_rows()
        file_name = self.get_file_name()
        response = self._get_csv_response(csv_rows, header, file_name)
        return response

    def _get_csv_response(self, csv_rows, header, file_name):
        return ExportAsCsv().export(csv_rows, header, file_name)

    def get_csv_rows(self):
        query = {'brand_model': self.order.brand_model, 'date': self.order.date,
                 'ranking_model': self.order.ranking_model}
        models = ModelExtractor(self.model_class, query, prefetch_keys=('product', 'warehouse', *self.extra_keys)).execute()
        csv_rows, header = self.convert_model_to_rows(models)
        return csv_rows, header

    @abstractmethod
    def get_file_name(self):
        pass

    @abstractmethod
    def get_model_class(self):
        pass

    @abstractmethod
    def convert_model_to_rows(self, models):
        pass

    def get_prefetch_keys(self):
        return ()


class ReplenishOrderDownloader(Downloader):
    def get_model_class(self):
        return ReplenishmentOrderModel

    def get_file_name(self):
        file_name = 'replenish_order_{brand}_{date}.csv'.format(brand=self.order.brand_model, date=self.order.date)
        return file_name

    def convert_model_to_rows(self, models):
        csv_rows = ModelConverter.convert_to_replenishment_order_rows(models)
        header = ['From Warehouse id', 'To Store id', 'Product/SKU', 'Replenishment Qty']
        return csv_rows, header

    def get_prefetch_keys(self):
        return ('store', )



class ShortQtyDownloader(Downloader):
    def get_model_class(self):
        return WarehouseProductShortQtyModel

    def get_file_name(self):
        file_name = 'short_qty_{brand}_{date}.csv'.format(brand=self.order.brand_model, date=self.order.date)
        return file_name

    def convert_model_to_rows(self, models):
        csv_rows = ModelConverter.convert_to_short_quantity_order_rows(models)
        header = ['Warehouse id', 'Product/SKU', 'Short Qty']
        return csv_rows, header


class ReportDownloadFactory:
    @staticmethod
    def get_downloader(report_type):
        if report_type == 'replenishorder':
            downloader = ReplenishOrderDownloader
        elif report_type == 'shortqtyorder':
            downloader = ShortQtyDownloader
        else:
            raise ValueError('Downloader not available for report-type: {}'.format(report_type))
        return downloader


class ExistingOrders(View):
    def get(self, request, brand_id):
        brand_model = self._get_brand_model(brand_id)
        if not brand_model:
            return HttpResponse('Brand Does not exists! Brand Id: {}'.format(brand_id))
        orders = self._get_orders(brand_id)
        context = {
            'brand_name': brand_model.name,
            'orders': orders
        }
        return render(request, 'order/view_orders.html', context)

    def post(self, request, brand_id):
        if not 'download_order' in request.POST:
            return HttpResponseRedirect(reverse('download_order', args=(brand_id,)))
        return OrderDownloadResponse(request).execute()

    def _get_brand_model(self, brand_id):
        brand_model = BrandModel.objects.filter(id=brand_id).first()
        return brand_model

    def _get_orders(self, brand_id):
        order_models = list(Order.objects.filter(brand_model__id=brand_id))
        return order_models
