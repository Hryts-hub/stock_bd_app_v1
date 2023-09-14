from django.contrib import admin

from components_app.models import StockComponents, StockFromExcel

# Register your models here.

admin.site.register(StockComponents)
admin.site.register(StockFromExcel)
