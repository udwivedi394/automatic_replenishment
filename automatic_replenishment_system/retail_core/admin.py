# vim: set fileencoding=utf-8 :
from django.contrib import admin

from automatic_replenishment_system.retail_core import models
from automatic_replenishment_system.retail_core.core.brand.brand_input_file_generator import BrandInputFileGenerator


class BrandModelAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'ranking_model',
    )
    search_fields = ('name',)
    # date_hierarchy = 'updated_at'
    actions = ['gen_input_files']

    def gen_input_files(self, request, queryset):
        store_inventory = 'input_data/Store_Inventory-1.csv'
        bsq = 'input_data/bsq-1.csv'
        store_priority_static = 'input_data/stores_priority_static.csv'
        output_product_list = 'input_data/one_time_data/product_list.csv'
        output_store_list = 'input_data/one_time_data/store_list.csv'
        output_warehouse_list = 'input_data/one_time_data/warehouse_list.csv'
        BrandInputFileGenerator(store_inventory, bsq, store_priority_static, output_product_list, output_store_list,
                                output_warehouse_list).execute()

    gen_input_files.short_description = 'Generate Input Files'


class ProductModelAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'product_code',
        'brand_model',
    )
    list_filter = ('brand_model',)
    # date_hierarchy = 'updated_at'


class StoreModelAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'store_code',
        'brand_model',
    )
    list_filter = ('brand_model',)
    # date_hierarchy = 'updated_at'


class WarehouseModelAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'warehouse_code',
    )
    list_filter = ('brand_model',)
    # date_hierarchy = 'updated_at'


class SalesTransactionAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'brand_model',
        'store',
        'product',
        'date',
        'quantity',
    )
    list_filter = (
        'brand_model',
        'store',
        'product',
        'date',
    )
    # date_hierarchy = 'updated_at'


class BSQAdmin(admin.ModelAdmin):
    list_display = (
        'id',

        'brand_model',
        'store',
        'product',
        'bsq',
    )
    list_filter = (
        'brand_model',
        'store',
        'product',
    )
    # date_hierarchy = 'updated_at'


class StoreInventoryModelAdmin(admin.ModelAdmin):
    list_display = (
        'id',

        'brand_model',
        'store',
        'product',
        'date',
        'closing_inventory',
    )
    list_filter = (
        'brand_model',
        'store',
        'product',
        'date',
    )
    # date_hierarchy = 'updated_at'


class WarehouseInventoryModelAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'brand_model',
        'product',
        'date',
        'closing_inventory',
    )
    list_filter = (
        'brand_model',
        'product',
        'date',
    )
    # date_hierarchy = 'updated_at'


class StaticPriorityModelAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'brand_model',
        'store',
        'static_priority_rank',
    )
    list_filter = ('brand_model', 'store')
    # date_hierarchy = 'updated_at'


class StoreWarehouseMappingModelAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'store',
        'warehouse',
    )


def _register(model, admin_class):
    admin.site.register(model, admin_class)


_register(models.BrandModel, BrandModelAdmin)
_register(models.ProductModel, ProductModelAdmin)
_register(models.StoreModel, StoreModelAdmin)
_register(models.WarehouseModel, WarehouseModelAdmin)
_register(models.SalesTransaction, SalesTransactionAdmin)
_register(models.BSQ, BSQAdmin)
_register(models.StoreInventoryModel, StoreInventoryModelAdmin)
_register(models.WarehouseInventoryModel, WarehouseInventoryModelAdmin)
_register(models.StaticPriorityModel, StaticPriorityModelAdmin)
_register(models.StoreWarehouseMappingModel, StoreWarehouseMappingModelAdmin)
