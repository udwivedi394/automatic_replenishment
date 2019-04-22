from django.contrib.postgres.fields import ArrayField
from django.db import models
# Create your models here.
from django.db.models import Model

from automatic_replenishment_system.retail_core.core.constants import RANKING_MODEL_CHOICES


class TimeStampedModel(Model):
    created_on = models.DateField(auto_now_add=True, db_index=True)
    updated_at = models.DateField(auto_now=True, db_index=True)

    class Meta:
        abstract = True


class BrandModel(TimeStampedModel):
    name = models.CharField(max_length=256, db_index=True)
    ranking_model = models.CharField(max_length=128, choices=RANKING_MODEL_CHOICES)

    class Meta:
        verbose_name = "Brand"
        verbose_name_plural = "Brands"

    def __str__(self):
        return "{name}".format(name=self.name)


class ProductModel(TimeStampedModel):
    product_code = models.CharField(max_length=256, db_index=True)
    brand_model = models.ForeignKey(BrandModel, models.CASCADE)

    class Meta:
        verbose_name = "Product"
        verbose_name_plural = "Products"

    def __str__(self):
        return "{} {}".format(self.brand_model, self.product_code)


class StoreModel(TimeStampedModel):
    store_code = models.CharField(max_length=256, db_index=True)
    brand_model = models.ForeignKey(BrandModel, models.CASCADE)

    class Meta:
        verbose_name = "Store"
        verbose_name_plural = "Stores"

    def __str__(self):
        return "{} {}".format(self.brand_model, self.store_code)


class WarehouseModel(TimeStampedModel):
    warehouse_code = models.CharField(max_length=256, db_index=True)
    brand_model = models.ForeignKey(BrandModel, models.CASCADE)

    class Meta:
        verbose_name = "Warehouse"
        verbose_name_plural = "Warehouses"

    def __str__(self):
        return "{} {}".format(self.brand_model, self.warehouse_code)


class SalesTransaction(TimeStampedModel):
    brand_model = models.ForeignKey(BrandModel, models.CASCADE)
    store = models.ForeignKey(StoreModel, models.CASCADE)
    product = models.ForeignKey(ProductModel, models.CASCADE)
    date = models.DateField()
    quantity = models.IntegerField()

    class Meta:
        verbose_name = "Sale Transaction"
        verbose_name_plural = "Sales Transactions"


class BSQModel(TimeStampedModel):
    brand_model = models.ForeignKey(BrandModel, models.CASCADE)
    store = models.ForeignKey(StoreModel, models.CASCADE)
    product = models.ForeignKey(ProductModel, models.CASCADE)
    bsq = models.IntegerField()

    class Meta:
        verbose_name = "BSQ"
        verbose_name_plural = "BSQ"


class StoreInventoryModel(TimeStampedModel):
    brand_model = models.ForeignKey(BrandModel, models.CASCADE)
    store = models.ForeignKey(StoreModel, models.CASCADE)
    product = models.ForeignKey(ProductModel, models.CASCADE)
    date = models.DateField()
    closing_inventory = models.IntegerField()

    class Meta:
        verbose_name = "Store Inventory"
        verbose_name_plural = "Store Inventory"


class WarehouseInventoryModel(TimeStampedModel):
    brand_model = models.ForeignKey(BrandModel, models.CASCADE)
    warehouse = models.ForeignKey(WarehouseModel, models.CASCADE, default=None, null=True)
    product = models.ForeignKey(ProductModel, models.CASCADE)
    date = models.DateField()
    closing_inventory = models.IntegerField()

    class Meta:
        verbose_name = "Warehouse Inventory"
        verbose_name_plural = "Warehouse Inventory"


class StaticPriorityModel(TimeStampedModel):
    brand_model = models.ForeignKey(BrandModel, models.CASCADE)
    store = models.ForeignKey(StoreModel, models.CASCADE)
    static_priority_rank = models.IntegerField()

    class Meta:
        verbose_name = "Static Priority"
        verbose_name_plural = "Static Priorities"


class StoreWarehouseMappingModel(TimeStampedModel):
    store = models.ForeignKey(StoreModel, models.CASCADE)
    warehouse = models.ForeignKey(WarehouseModel, models.CASCADE)


class Order(TimeStampedModel):
    brand_model = models.ForeignKey(BrandModel, models.CASCADE)
    ranking_model = models.CharField(max_length=128, choices=RANKING_MODEL_CHOICES)
    date = models.DateField()
    completed = models.BooleanField(default=False)


class ReplenishmentOrderModel(TimeStampedModel):
    brand_model = models.ForeignKey(BrandModel, models.CASCADE)
    ranking_model = models.CharField(max_length=128, choices=RANKING_MODEL_CHOICES)
    date = models.DateField()
    warehouse = models.ForeignKey(WarehouseModel, models.CASCADE)
    store = models.ForeignKey(StoreModel, models.CASCADE)
    product = models.ForeignKey(ProductModel, models.CASCADE)
    replenishment_qty = models.IntegerField()

    class Meta:
        verbose_name = "Replenishment Order"
        verbose_name_plural = "Replenishment Orders"


class WarehouseProductShortQtyModel(TimeStampedModel):
    brand_model = models.ForeignKey(BrandModel, models.CASCADE)
    ranking_model = models.CharField(max_length=128, choices=RANKING_MODEL_CHOICES)
    date = models.DateField()
    warehouse = models.ForeignKey(WarehouseModel, models.CASCADE)
    product = models.ForeignKey(ProductModel, models.CASCADE)
    short_qty = models.IntegerField()

    class Meta:
        verbose_name = "Warehouse Short Quantity"
        verbose_name_plural = "Warehouse Short Quantities"


class FileModel(TimeStampedModel):
    file_type = models.CharField(max_length=128)
    file = models.FileField(upload_to='reviews/', blank=True)


class FileHandler(TimeStampedModel):
    file_list = ArrayField(models.IntegerField(), blank=True)
