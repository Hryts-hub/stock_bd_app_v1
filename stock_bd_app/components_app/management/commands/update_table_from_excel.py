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

    help = 'Creates new rows and Updates changed ones'

    def add_arguments(self, parser):
        parser.add_argument('model_app_name', type=str, help='Name of the app of the model')
        parser.add_argument('model_name', type=str, help='Name of the model of the Table')

    def handle(self, *args, **options):
        model_app_name = options['model_app_name']
        model_name = options['model_name']

        print(model_app_name, model_name)
        try:
            model = apps.get_model(model_app_name, model_name)
        except LookupError:
            self.stdout.write(self.style.ERROR('Model not found'))
            return

        start_time = time.time()
        mem_before = psutil.virtual_memory().used

        # StockTabFromExcelUpdater(
        #     model, PATH_TO_FILE_STOCK, FILE_STOCK, SHEET_NAME, COLUMNS
        # ).update_and_create_by_iterrows()
        # StockTabFromExcelUpdater(
        #     model, PATH_TO_FILE_STOCK, FILE_STOCK, SHEET_NAME, COLUMNS
        # ).update_and_create_by_itertuples()
        StockTabFromExcelUpdater(
            model, PATH_TO_FILE_STOCK, FILE_STOCK, SHEET_NAME, COLUMNS
        ).update_of_db()

        end_time = time.time()
        mem_after = psutil.virtual_memory().used

        print("ALL DONE !!!")
        print("Time for create-update:", end_time - start_time, "seconds")
        print("Memory used by create-update:", mem_after - mem_before, "bytes")

