import pandas as pd
import numpy as np
from django.test import TestCase

from components_app.management.commands.update_table_from_excel import FILE_STOCK, SHEET_NAME
from components_app.services import StockTabFromExcelUpdater, DataReader
from components_app.models import StockFromExcel, DEFAULT_NAN_VALUE
import os

import openpyxl

# TEST_FILE_1 = 'Склад 14.01.16.xlsx'
TEST_FILE_1 = 'file_data_created.xlsx'
TEST_FILE_2 = 'file_data_updated.xlsx'

TEST_FOLDER = 'test_data/'

TEST_EXCEL_PATH_1 = os.path.abspath(os.path.join(os.path.dirname(__file__), TEST_FOLDER, TEST_FILE_1))
TEST_EXCEL_PATH_2 = os.path.abspath(os.path.join(os.path.dirname(__file__), TEST_FOLDER, TEST_FILE_2))

PATH_TO_TEST_DATA = os.path.join(os.path.dirname(__file__), TEST_FOLDER)

# __file__  --> represents the file the code is executing from
# os.path.dirname(__file__)  --> gives you the directory the file is in
# join  --> joins two path-strings (slash saved at the end of the path-str)
# os.path.abspath  --> gives you an absolute path
# (normalized path with similar slashes in path-str and NO slash at the end of the path-str)

# COLUMNS = 'C, D, E, F, G, H, I, J, K, L, M, N, O, P'
# COLUMNS_TO_FILE = 'A, B, C, D'
COLUMNS = 'C, D, E, F, G, H, I, J, K, L, M, N, O'
# SHEET_NAME = 'Склад'
# FILE_STOCK = 'Склад 14.01.16.xlsx'
MODEL = StockFromExcel

# COMMANDS
# python manage.py test components_app


class ServicesTestCase(TestCase):
    # data for creating
    data_dict_for_test_excel_file_1 = {
        'Переход в Резервы': ['>>', '>>', '>>', '>>'],
        'Переход в СП плат': ['>>', '>>', '>>', '>>'],
        'Артикул': [None, 3, None, 5],
        'Тип': [None, 'УСТАРЕЛО', None, 'УСТАРЕЛО'],
        'Вид': [None, 'К-р - конденсаторы', None, 'К-р - конденсаторы'],
        'Подвид': [None, 'пленочные', None, 'пленочные'],
        'Название\n(Комплектующие склада)': [None, '0,22uF 2k Vdc 10%', None, '2,2uF 305Vac'],
        '        Корпус                    DIN (для механики)': [
            None, 'L/S 37,5 42x16x28,5', None, 'L/S 27,5 18x28x31'],
        'Склад основной': [None, 19, None, 0],
        'Доступно\nк выдаче': [None, 19.0, None, 0],
        'Цена, $': [None, None, None, 0.9],
        'PART Number': [None, 'B32656J224K', None, 'PCX2 339L 61225'],
        'Производитель': [None, 'EPCOS (TDK)', None, 'PILKOR'],
        'Part number #2': [None, None, None, None],
        'Производитель #2': [None, None, None, None],

    }

    # data for updating (last row is all None - should not be written to the db)
    data_dict_for_test_excel_file_2 = {
        'Переход в Резервы': ['>>', '>>', '>>', '>>', '>>', '>>'],
        'Переход в СП плат': ['>>', '>>', '>>', '>>', '>>', '>>'],
        'Артикул': [None, 3, 4, 5, 6, None],
        'Тип': [None, 'УСТАРЕЛО', 'Э - электроника', 'Э - электроника', 'Э - электроника', None],
        'Вид': [None, 'К-р - конденсаторы', 'К-р - конденсаторы', 'Рзн - разное', 'Сль - соединитель', None],
        'Подвид': [None, 'пленочные', 'пленочные', 'стяжка', 'втулка', None],
        'Название\n(Комплектующие склада)': [
            None, '0,22uF 2k Vdc 10%', '2,7uF ...bla-bla', '2,2uF 305Vac', 'bla-bla', None],
        '        Корпус                    DIN (для механики)': [
            None, 'L/S 37,5 42x16x28,5', '31,5x14x28', None, None, None],
        'Склад основной': [None, 19, 14, None, None, None],
        'Доступно\nк выдаче': [None, 19.0, 14, None, None, None],
        'Цена, $': [None, None, 3.07, 0.9, None, None],
        'PART Number': [
            None, 'B32656J224K', '1PCX2 339L 61225', 'PCX2 339L 61225', '2PCX2 339L 61225', None],
        'Производитель': [None, 'EPCOS (TDK)', 'KEMET', None, 'DREMEC', None],
        'Part number #2': [None, None, None, None, None, None],
        'Производитель #2': [None, None, None, None, None, None],

    }
    excel_column_names = data_dict_for_test_excel_file_1.keys()
    column_names_to_read_from_excel = list(excel_column_names)[2:]

    dataframe_for_excel_file_1 = pd.DataFrame(data_dict_for_test_excel_file_1)
    dataframe_for_excel_file_2 = pd.DataFrame(data_dict_for_test_excel_file_2)

    full_path_1 = TEST_EXCEL_PATH_1
    full_path_2 = TEST_EXCEL_PATH_2

    file_name_1 = TEST_FILE_1
    file_name_2 = TEST_FILE_2

    path_to_file = PATH_TO_TEST_DATA
    sheet_name = SHEET_NAME
    columns_letters_str = COLUMNS
    longer_columns_letters_str = 'C, D, E, F, G, H, I, J, K, L, M, N, O, QQ'
    err_columns_letters_str = 'err'

    model = MODEL

    nan_value = DEFAULT_NAN_VALUE

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # print()
        # print('-----test-DF to write into the excel file')
        # print(cls.dataframe_for_excel_file.head())
        # print(f'cls.test_path = {cls.full_path}')

        cls.dataframe_for_excel_file_1.to_excel(
            cls.full_path_1,
            sheet_name=cls.sheet_name,
            na_rep='',
            index=False,
            startrow=0,
            engine='openpyxl',
        )
        cls.dataframe_for_excel_file_2.to_excel(
            cls.full_path_2,
            sheet_name=cls.sheet_name,
            na_rep='',
            index=False,
            startrow=0,
            engine='openpyxl',
        )

        # print('-----test_df 1, 2 created')

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()

        # Clean up by deleting the test Excel file
        if os.path.exists(cls.full_path_1):
            try:
                os.remove(cls.full_path_1)
            except Exception as e:
                print(f'ОШИБКА tearDownClass1: {type(e)}: {e}')
        if os.path.exists(cls.full_path_2):
            try:
                os.remove(cls.full_path_2)
            except Exception as e:
                print(f'ОШИБКА tearDownClass2: {type(e)}: {e}')
        # print('-----test_excel_files removed')

    @classmethod
    def setUpTestData(cls):
        """Load initial data for the TestCase."""
        # Create initial test data shared among all test methods -
        # create test data in DB
        pass

    def setUp(self):
        # Setup specific to each test method
        pass

    def tearDown(self):
        # Teardown specific to each test method
        self.model.objects.all().delete()
        # print('-----Teardown specific to each test method')
        pass

    def test_make_cell_names(self):
        letters_str = 'A, B, C'
        cell_names = StockTabFromExcelUpdater.make_cell_names(letters_str)
        self.assertEqual(cell_names, ['A1', 'B1', 'C1'])

    def test_validate_columns_true(self):
        flag = StockTabFromExcelUpdater(
            self.model,
            self.path_to_file,
            self.file_name_1,
            self.sheet_name,
            self.columns_letters_str).validate_columns()

        self.assertEqual(True, flag)

        # print('-----test_validate_columns_true')

    def test_validate_columns_false(self):
        flag = StockTabFromExcelUpdater(
            self.model,
            self.path_to_file,
            self.file_name_1,
            self.sheet_name,
            self.longer_columns_letters_str).validate_columns()

        self.assertEqual(False, flag)

        # print('-----test_validate_columns_false')

    def test_validate_columns_err(self):
        flag = StockTabFromExcelUpdater(
            self.model,
            self.path_to_file,
            self.file_name_1,
            self.sheet_name,
            self.err_columns_letters_str).validate_columns()

        self.assertEqual(False, flag)

        # print('-----test_validate_columns_err')

    def test_read_specified_columns_from_db_table_initial_state(self):

        init_test_obj = StockTabFromExcelUpdater(
            self.model,
            self.path_to_file,
            self.file_name_1,
            self.sheet_name,
            self.columns_letters_str)

        db_df = init_test_obj.read_specified_columns_from_db_table()

        self.assertEqual(len(db_df), 0)

        # print('-----test_read_specified_columns_from_db_table 0')

    def test_read_specified_columns_from_db_table_1row(self):
        # create 1 row in table with default values
        self.model.objects.create()

        init_test_obj = StockTabFromExcelUpdater(
            self.model,
            self.path_to_file,
            self.file_name_1,
            self.sheet_name,
            self.columns_letters_str)

        db_df = init_test_obj.read_specified_columns_from_db_table()

        self.assertEqual(len(db_df), 1)

        # print('-----test_read_specified_columns_from_db_table_1row')

    def test_read_specified_columns_from_excel_sheet_success(self):
        init_test_obj = StockTabFromExcelUpdater(
            self.model,
            self.path_to_file,
            self.file_name_1,
            self.sheet_name,
            self.columns_letters_str)

        source_df = init_test_obj.read_specified_columns_from_excel_sheet(np.nan)
        # check if all values in a pandas DataFrame have a string type (str)
        # use .all() twice to check if all values in the resulting DataFrame are True.
        all_str = source_df.applymap(lambda x: isinstance(x, str)).all().all()

        self.assertEqual(source_df.shape,
                         (len(self.dataframe_for_excel_file_1), len(init_test_obj.col_list))
                         )
        self.assertEqual(all_str, True)

        # print('-----test_read_specified_columns_from_excel_sheet_success')

    def test_validate_df_to_get_unequal_rows_create(self):
        init_test_obj = StockTabFromExcelUpdater(
            self.model,
            self.path_to_file,
            self.file_name_1,
            self.sheet_name,
            self.columns_letters_str)
        unequal_rows = init_test_obj.validate_df_to_get_unequal_rows()
        # equals -- This approach directly compares the content of the two DataFrames,
        # considering index, column names, and cell values.
        # It's a more reliable way to determine whether the DataFrames are the same.
        res = unequal_rows.equals(init_test_obj.read_specified_columns_from_excel_sheet(np.nan))
        self.assertEqual(res, True)
        # print('-----test_validate_df_to_get_unequal_rows_create')

    def test_validate_df_to_get_unequal_rows_update(self):

        init_test_obj_1 = StockTabFromExcelUpdater(
            self.model,
            self.path_to_file,
            self.file_name_1,
            self.sheet_name,
            self.columns_letters_str)
        unequal_rows_1 = init_test_obj_1.validate_df_to_get_unequal_rows()
        # iterrows and itertuples give the same results.
        # so for testing we use different methods to catch the changes and mistakes
        # upon modifying functions
        init_test_obj_1.create_by_iterrows(unequal_rows_1)

        init_test_obj_2 = StockTabFromExcelUpdater(
            self.model,
            self.path_to_file,
            self.file_name_2,
            self.sheet_name,
            self.columns_letters_str)
        # 1st run - returns rows of unequal_idxs, if all idxs equals --> returns unequal_rows
        unequal_idxs_2 = init_test_obj_2.validate_df_to_get_unequal_rows()
        self.assertEqual(len(unequal_idxs_2), 1)
        # print('-----test_validate_df_to_get_unequal_rows_update')

    def test_create_by_iterrows(self):
        init_test_obj_1 = StockTabFromExcelUpdater(
            self.model,
            self.path_to_file,
            self.file_name_1,
            self.sheet_name,
            self.columns_letters_str)
        unequal_rows_1 = init_test_obj_1.validate_df_to_get_unequal_rows()
        res = init_test_obj_1.create_by_iterrows(unequal_rows_1)
        self.assertEqual(res, (4, 0))

    def test_create_by_itertuples(self):
        init_test_obj_1 = StockTabFromExcelUpdater(
            self.model,
            self.path_to_file,
            self.file_name_1,
            self.sheet_name,
            self.columns_letters_str)
        unequal_rows_1 = init_test_obj_1.validate_df_to_get_unequal_rows()
        res = init_test_obj_1.create_by_itertuples(unequal_rows_1)
        self.assertEqual(res, (4, 0))

    def test_update_and_create_by_iterrows(self):
        init_test_obj_1 = StockTabFromExcelUpdater(
            self.model,
            self.path_to_file,
            self.file_name_1,
            self.sheet_name,
            self.columns_letters_str)
        unequal_rows_1 = init_test_obj_1.validate_df_to_get_unequal_rows()
        init_test_obj_1.create_by_iterrows(unequal_rows_1)

        init_test_obj_2 = StockTabFromExcelUpdater(
            self.model,
            self.path_to_file,
            self.file_name_2,
            self.sheet_name,
            self.columns_letters_str)

        res = init_test_obj_2.update_and_create_by_iterrows()
        self.assertEqual(res, (1, 0, 2, 0))

    def test_update_and_create_by_itertuples(self):
        init_test_obj_1 = StockTabFromExcelUpdater(
            self.model,
            self.path_to_file,
            self.file_name_1,
            self.sheet_name,
            self.columns_letters_str)
        unequal_rows_1 = init_test_obj_1.validate_df_to_get_unequal_rows()
        init_test_obj_1.create_by_iterrows(unequal_rows_1)

        init_test_obj_2 = StockTabFromExcelUpdater(
            self.model,
            self.path_to_file,
            self.file_name_2,
            self.sheet_name,
            self.columns_letters_str)

        res = init_test_obj_2.update_and_create_by_itertuples()
        self.assertEqual(res, (1, 0, 2, 0))

    def test_update_and_create_by_itertuples_err(self):
        init_test_obj_1 = StockTabFromExcelUpdater(
            self.model,
            self.path_to_file,
            self.file_name_1,
            self.sheet_name,
            self.columns_letters_str)
        unequal_rows_1 = init_test_obj_1.validate_df_to_get_unequal_rows()
        init_test_obj_1.create_by_iterrows(unequal_rows_1)

        init_test_obj_2 = StockTabFromExcelUpdater(
            self.model,
            self.path_to_file,
            self.file_name_2,
            self.sheet_name,
            self.longer_columns_letters_str)

        res = init_test_obj_2.update_and_create_by_itertuples()
        self.assertEqual(res, (0, 0, 0, 0))

