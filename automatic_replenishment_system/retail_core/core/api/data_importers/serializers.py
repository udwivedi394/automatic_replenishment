from rest_framework import serializers

from automatic_replenishment_system.retail_core.core.constants import RANKING_MODEL_CHOICES


class BrandRowSerializer(serializers.Serializer):
    value = serializers.CharField(max_length=20000, required=True)

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass


class WarehouseRowSerializer(serializers.Serializer):
    store_code = serializers.CharField(max_length=20000, required=True)
    warehouse_code = serializers.CharField(max_length=20000, required=True)

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass


class BrandInputSerializer(serializers.Serializer):
    name = serializers.CharField(required=True)
    ranking_model = serializers.ChoiceField(choices=RANKING_MODEL_CHOICES)
    stores = serializers.ListField(child=BrandRowSerializer(), required=True)
    warehouses = serializers.ListField(child=BrandRowSerializer(), required=True)
    products = serializers.ListField(child=BrandRowSerializer(), required=True)

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass
