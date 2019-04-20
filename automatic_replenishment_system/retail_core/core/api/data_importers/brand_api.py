import json

from django.db import transaction
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from rest_framework.exceptions import APIException
from rest_framework.views import APIView

from automatic_replenishment_system.retail_core.core.api.data_importers.brand_api_processor import \
    BrandCreationProcessor


@method_decorator(transaction.non_atomic_requests, name='dispatch')
class BrandCreator(APIView):
    def post(self, request):
        try:
            self._process_request(request)
            response_dict = {'message': 'success'}
            response_json = json.dumps(response_dict)
        except Exception as e:
            raise APIException(str(e))
        return HttpResponse(response_json, status=200)

    def _process_request(self, request):
        BrandCreationProcessor().execute(request)
