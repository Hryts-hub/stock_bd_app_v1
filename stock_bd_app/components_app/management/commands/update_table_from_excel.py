import time
import psutil

from django.core.management import BaseCommand
from components_app.services import StockTabFromExcelUpdater
from django.apps import apps

# import os
# from dotenv import load_dotenv
# load_dotenv()


# COLUMNS = 'C, D, E, F, G, H, I, J, K, L, M, N, O'
COLUMNS = 'C, D, E, F, G, H, I, J, K, L, M, N, O, P'

SHEET_NAME = 'Склад'

FILE_STOCK = 'Склад 14.01.16.xlsx'

# PATH_TO_FILE_STOCK = os.getenv("PATH_TO_FILE_STOCK")
# PATH_TO_FILE_STOCK = 'D:/OEMTECH/Projects/FILE_STOCK_FOLDER/stock_versions/stock_4856/'
# PATH_TO_FILE_STOCK = 'D:/OEMTECH/Projects/FILE_STOCK_FOLDER/stock_versions/stock_4894/'
# PATH_TO_FILE_STOCK = 'D:/OEMTECH/Projects/FILE_STOCK_FOLDER/stock_versions/stock_4978/'
# PATH_TO_FILE_STOCK = 'D:/OEMTECH/Projects/FILE_STOCK_FOLDER/stock_versions/stock_4982/'
PATH_TO_FILE_STOCK = 'D:/OEMTECH/Projects/FILE_STOCK_FOLDER/stock_versions/stock_4989/'

# COMMANDS

# # Python manage.py update_table_from_excel StockFromExcel
#
# Python manage.py update_table_from_excel components_app StockFromExcel
#
# python manage.py clear_table StockFromExcel


class Command(BaseCommand):

    # def handle(self, *args, **kwargs):
    #     # StockTabFromExcelUpdater().get_db_tab_names()
    #     StockTabFromExcelUpdater().get_db_tab_columns()

    help = 'Creates new rows and Updates changed ones'

    def add_arguments(self, parser):
        parser.add_argument('model_app_name', type=str, help='Name of the app of the model')
        parser.add_argument('model_name', type=str, help='Name of the model of the Table')
        # parser.add_argument('model_app_name', type=str, help='Name of the app of the model')

    def handle(self, *args, **options):
        model_app_name = options['model_app_name']
        model_name = options['model_name']

        print(model_app_name, model_name)
        try:
            # model = apps.get_model('components_app', model_name)
            model = apps.get_model(model_app_name, model_name)
            # print(1)
            # print(model._meta.get_fields())
            # print(2)
            # print(type(model._meta.get_fields()))
            # print()
        except LookupError:
            self.stdout.write(self.style.ERROR('Model not found'))
            return

        #print(model)

        start_time = time.time()
        mem_before = psutil.virtual_memory().used

        # clear_table_records(model)
        # self.stdout.write(self.style.SUCCESS(f'All records cleared for model {model_name}'))

        # tab_name = f'components_app_{model_name.lower()}'
        # StockTabFromExcelUpdater().get_db_tab_columns(tab_name)
        # StockTabFromExcelUpdater().get_verbose_column_names(model)

        # StockTabFromExcelUpdater(model, SHEET_NAME, COLUMNS).validate_columns()
        # StockTabFromExcelUpdater(model, SHEET_NAME, COLUMNS).get_df_with_changes()
        # StockTabFromExcelUpdater(model, SHEET_NAME, COLUMNS).create_by_iterrows()

        # StockTabFromExcelUpdater(
        #     model, PATH_TO_FILE_STOCK, FILE_STOCK, SHEET_NAME, COLUMNS
        # ).update_and_create_by_iterrows()
        StockTabFromExcelUpdater(
            model, PATH_TO_FILE_STOCK, FILE_STOCK, SHEET_NAME, COLUMNS
        ).update_and_create_by_itertuples()

        end_time = time.time()
        mem_after = psutil.virtual_memory().used

        print("ALL DONE !!!")
        print("Time for create-update:", end_time - start_time, "seconds")
        print("Memory used by create-update:", mem_after - mem_before, "bytes")

