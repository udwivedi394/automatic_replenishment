from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import CharField, Model
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

from automatic_replenishment_system.retail_core.core.constants import RANKING_MODEL_CHOICES


class User(AbstractUser):
    # First Name and Last Name do not cover name patterns
    # around the globe.
    name = CharField(_("Name of User"), blank=True, max_length=255)

    def get_absolute_url(self):
        return reverse("users:detail", kwargs={"username": self.username})


class TimeStampedModel(Model):
    created_on = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True, db_index=True)

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


class StoreModel(TimeStampedModel):
    store_code = models.CharField(max_length=256, db_index=True)
    brand_model = models.ForeignKey(BrandModel, models.CASCADE)

    class Meta:
        verbose_name = "Store"
        verbose_name_plural = "Stores"


class WarehouseModel(TimeStampedModel):
    warehouse_code = models.CharField(max_length=256, db_index=True)
    brand_model = models.ForeignKey(BrandModel, models.CASCADE)

    class Meta:
        verbose_name = "Warehouse"
        verbose_name_plural = "Warehouses"


class SalesTransaction(TimeStampedModel):
    brand_model = models.ForeignKey(BrandModel, models.CASCADE)
    store = models.ForeignKey(StoreModel, models.CASCADE)
    product = models.ForeignKey(ProductModel, models.CASCADE)
    date = models.DateTimeField()
    quantity = models.IntegerField()

    class Meta:
        verbose_name = "Sale Transaction"
        verbose_name_plural = "Sales Transactions"


class BSQ(TimeStampedModel):
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
    date = models.DateTimeField()
    closing_inventory = models.IntegerField()

    class Meta:
        verbose_name = "Store Inventory"
        verbose_name_plural = "Store Inventory"


class WarehouseInventoryModel(TimeStampedModel):
    brand_model = models.ForeignKey(BrandModel, models.CASCADE)
    product = models.ForeignKey(ProductModel, models.CASCADE)
    date = models.DateTimeField()
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


class StoreWarehouseBinding(TimeStampedModel):
    brand_model = models.ForeignKey(BrandModel, models.CASCADE)
    store = models.ForeignKey(StoreModel, models.CASCADE)
    warehouse = models.ForeignKey(WarehouseModel, models.CASCADE)
