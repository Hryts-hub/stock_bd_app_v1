# Generated by Django 4.1.7 on 2023-08-25 10:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('components_app', '0006_alter_stockfromexcel_art_number'),
    ]

    operations = [
        migrations.AlterField(
            model_name='stockfromexcel',
            name='art_number',
            field=models.CharField(blank=True, default='', help_text='Поле - Аритикул - в файле склада.', max_length=250, null=True, verbose_name='Артикул'),
        ),
    ]