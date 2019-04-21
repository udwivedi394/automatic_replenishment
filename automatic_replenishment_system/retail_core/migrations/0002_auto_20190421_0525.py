# Generated by Django 2.0.13 on 2019-04-21 05:25

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('retail_core', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='StoreWarehouseMappingModel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_on', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated_at', models.DateTimeField(auto_now=True, db_index=True)),
                ('store', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='retail_core.StoreModel')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.RemoveField(
            model_name='warehousemodel',
            name='store',
        ),
        migrations.AddField(
            model_name='storewarehousemappingmodel',
            name='warehouse',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='retail_core.WarehouseModel'),
        ),
    ]
