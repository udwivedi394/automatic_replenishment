class RankingModel:
    STATIC = 'static'
    DYNAMIC = 'dynamic'


RANKING_MODEL_CHOICES = (
    (RankingModel.STATIC, 'Static'),
    (RankingModel.DYNAMIC, 'Dynamic'),
)


class WarehouseConstants:
    DEFAULT_WAREHOUSE_CODE = 'WH001'


class BrandFilesConstants:
    STORE_CODE = 'Store_Code'
    PRODUCT_CODE = 'Product_Code'
    WAREHOUSE_CODE = 'Warehouse_Code'
