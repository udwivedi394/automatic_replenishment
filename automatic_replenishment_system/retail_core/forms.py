from django import forms
from material import Layout, Row

from automatic_replenishment_system.retail_core.models import BrandModel


class BrandForm(forms.ModelForm):
    class Meta:
        model = BrandModel
        exclude = ()
        labels = {
            'name': 'Brand Name',
            'ranking_model': 'Ranking Model',
        }

    layout = Layout(Row('name',
                        'ranking_model'))


class ProductForm(forms.Form):
    products_file = forms.FileField()
    layout = Layout(Row('products_file'))


class StoreForm(forms.Form):
    stores_file = forms.FileField()
    layout = Layout(Row('stores_file'))


class WarehouseForm(forms.Form):
    warehouse_file = forms.FileField()
    layout = Layout(Row('warehouse_file'))


class StoreStaticRankForm(forms.Form):
    static_rank_file = forms.FileField()
    layout = Layout(Row('static_rank_file'))


class BrandViewForm(forms.ModelForm):
    class Meta:
        model = BrandModel
        fields = ('ranking_model',)

    layout = Layout(Row('ranking_model'))


class GenerateOrderForm(forms.Form):
    generation_date = forms.DateField()
    bsq = forms.FileField()
    sales_transactions = forms.FileField()
    store_inventory = forms.FileField()
    warehouse_inventory = forms.FileField()

    layout = Layout(Row('generation_date'),
                    Row('bsq'), Row('sales_transactions'), Row('store_inventory'), Row('warehouse_inventory'), )
