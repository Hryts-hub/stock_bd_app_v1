# Generated by Django 4.1.7 on 2023-08-18 14:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('components_app', '0005_alter_stockfromexcel_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='stockfromexcel',
            name='art_number',
            field=models.FloatField(blank=True, help_text='Поле - Аритикул - в файле склада.', null=True, verbose_name='Артикул'),
        ),
    ]
