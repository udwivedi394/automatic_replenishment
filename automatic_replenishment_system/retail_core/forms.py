from django import forms
from material import Layout, Row

from automatic_replenishment_system.users.models import BrandModel, StoreModel


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
    # class Meta:
    #     labels = {
    #         'products_file': 'Products File',
    #     }

    products_file = forms.FileField()
    layout = Layout(Row('products_file'))


class StoreForm(forms.Form):
    # class Meta:
    #     labels = {
    #         'stores_file': 'Stores File',
    #     }

    stores_file = forms.FileField()

    layout = Layout(Row('stores_file'))


class WarehouseForm(forms.Form):
    # class Meta:
    #     labels = {
    #         'warehouse_file': 'Warehouse File',
    #     }

    warehouse_file = forms.FileField()

    layout = Layout(Row('warehouse_file'))
