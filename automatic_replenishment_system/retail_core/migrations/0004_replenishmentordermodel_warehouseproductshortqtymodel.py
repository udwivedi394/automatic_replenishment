# Generated by Django 2.0.13 on 2019-04-22 08:23

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('retail_core', '0003_auto_20190421_1318'),
    ]

    operations = [
        migrations.CreateModel(
            name='ReplenishmentOrderModel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_on', models.DateField(auto_now_add=True, db_index=True)),
                ('updated_at', models.DateField(auto_now=True, db_index=True)),
                ('ranking_model', models.CharField(choices=[('static', 'Static'), ('dynamic', 'Dynamic')], max_length=128)),
                ('date', models.DateField()),
                ('replenishment_qty', models.IntegerField()),
                ('brand_model', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='retail_core.BrandModel')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='retail_core.ProductModel')),
                ('store', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='retail_core.StoreModel')),
                ('warehouse', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='retail_core.WarehouseModel')),
            ],
            options={
                'verbose_name': 'Replenishment Order',
                'verbose_name_plural': 'Replenishment Orders',
            },
        ),
        migrations.CreateModel(
            name='WarehouseProductShortQtyModel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_on', models.DateField(auto_now_add=True, db_index=True)),
                ('updated_at', models.DateField(auto_now=True, db_index=True)),
                ('ranking_model', models.CharField(choices=[('static', 'Static'), ('dynamic', 'Dynamic')], max_length=128)),
                ('date', models.DateField()),
                ('short_qty', models.IntegerField()),
                ('brand_model', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='retail_core.BrandModel')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='retail_core.ProductModel')),
                ('warehouse', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='retail_core.WarehouseModel')),
            ],
            options={
                'verbose_name': 'Warehouse Short Quantity',
                'verbose_name_plural': 'Warehouse Short Quantities',
            },
        ),
    ]