from rest_framework import serializers

from automatic_replenishment_system.retail_core.core.constants import RANKING_MODEL_CHOICES


class StoreRowSerializer(serializers.Serializer):
    Store_Code = serializers.CharField(max_length=20000, required=True)

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass


class ProductRowSerializer(serializers.Serializer):
    Product_Code = serializers.CharField(max_length=20000, required=True)

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass


class WarehouseRowSerializer(serializers.Serializer):
    Store_Code = serializers.CharField(max_length=20000, required=True)
    Warehouse_Code = serializers.CharField(max_length=20000, required=True)

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass


class BrandInputSerializer(serializers.Serializer):
    name = serializers.CharField(required=True)
    ranking_model = serializers.ChoiceField(choices=RANKING_MODEL_CHOICES)
    stores = serializers.ListField(child=StoreRowSerializer(), required=True)
    products = serializers.ListField(child=ProductRowSerializer(), required=True)
    warehouses = serializers.ListField(child=WarehouseRowSerializer(), required=True)

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass
