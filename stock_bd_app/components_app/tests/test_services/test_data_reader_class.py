import pandas as pd
from django.test import TestCase

from components_app.management.commands.update_table_from_excel import FILE_STOCK, SHEET_NAME
from components_app.services import DataReader
import os
import openpyxl

# TEST_FILE_1 = 'Склад 14.01.16.xlsx'
TEST_FILE_1 = FILE_STOCK
TEST_FOLDER = 'test_data/'
TEST_EXCEL_PATH_1 = os.path.abspath(os.path.join(os.path.dirname(__file__), TEST_FOLDER, TEST_FILE_1))
PATH_TO_TEST_DATA = os.path.join(os.path.dirname(__file__), TEST_FOLDER)

# __file__  --> represents the file the code is executing from
# os.path.dirname(__file__)  --> gives you the directory the file is in
# join  --> joins two path-strings (slash saved at the end of the path-str)
# os.path.abspath  --> gives you an absolute path
# (normalized path with similar slashes in path-str and NO slash at the end of the path-str)

# COLUMNS = 'C, D, E, F, G, H, I, J, K, L, M, N, O, P'
# COLUMNS_TO_FILE = 'A, B, C, D'
COLUMNS = 'C, D'
# SHEET_NAME = 'Склад'
# FILE_STOCK = 'Склад 14.01.16.xlsx'

# COMMANDS
# python manage.py test components_app


class ServicesTestCase(TestCase):
    data_dict_for_test_excel_file = {
        'Переход в Резервы': ['>>', '>>', '>>', '>>', '>>'],
        'Переход в СП плат': ['>>', '>>', '>>', '>>', '>>'],
        'Артикул': [None, None, None, 4, 5],
        'Тип': [None, None, None, None, 'УСТАРЕЛО']
    }
    test_excel_column_names = data_dict_for_test_excel_file.keys()
    column_names_to_read_from_excel = list(test_excel_column_names)[2:]
    dataframe_for_excel_file = pd.DataFrame(data_dict_for_test_excel_file)
    full_path = TEST_EXCEL_PATH_1
    file_name = TEST_FILE_1
    path_to_file = PATH_TO_TEST_DATA
    sheet_name = SHEET_NAME
    columns_letters_str = COLUMNS

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # print()
        # print('-----test-DF to write into the excel file')
        # print(cls.dataframe_for_excel_file.head())
        # print(f'cls.test_path = {cls.full_path}')

        cls.dataframe_for_excel_file.to_excel(
            cls.full_path,
            sheet_name=cls.sheet_name,
            na_rep='',
            index=False,
            startrow=0,
            engine='openpyxl',
        )

        # print('-----test_df created')

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()

        # Clean up by deleting the test Excel file
        if os.path.exists(cls.full_path):
            os.remove(cls.full_path)
        # print('-----test_excel_file removed')

    @classmethod
    def setUpTestData(cls):
        """Load initial data for the TestCase."""
        # Create initial test data shared among all test methods -
        # create test data in DB
        # Set up non-modified objects used by all test methods
        pass

    def setUp(self):
        # Setup specific to each test method
        pass

    def tearDown(self):
        # Teardown specific to each test method
        pass

    def test_read_excel_to_dataframe_success(self):
        # print()
        # print('-----test_read_excel_to_dataframe_success')
        # print('---DF read from excel file')
        df = pd.read_excel(
                    self.full_path,
                    sheet_name=self.sheet_name,
                    usecols=self.columns_letters_str,
                    engine='openpyxl',
                    dtype='object',
                )
        # print(df.head())
        # print(df.shape)
        # print()
        #
        # print('--- test DataReader, read_data_from_stock_file')
        source_df, msg = DataReader(
            self.path_to_file, self.file_name).read_data_from_stock_file(
            self.sheet_name, self.columns_letters_str)
        # print(source_df.head())
        are_equal = df.equals(source_df)

        self.assertEqual(are_equal, True)
        self.assertEqual(msg, '')

    def test_read_excel_to_dataframe_fail(self):
        # print()
        # print('-----test_read_excel_to_dataframe_fail')
        # print('---DF read from excel file')
        df = pd.read_excel(
                    self.full_path,
                    sheet_name=self.sheet_name,
                    usecols=self.columns_letters_str,
                    engine='openpyxl',
                    dtype='object',
                )
        # print(df.head())
        # print(df.shape)
        # print()

        # print('--- test DataReader, read_data_from_stock_file')
        # print('--fail_path')
        source_df, msg = DataReader(
            'fail_path/', self.file_name).read_data_from_stock_file(
            self.sheet_name, self.columns_letters_str)
        are_equal = df.equals(source_df)

        self.assertEqual(are_equal, False)
        self.assertEqual(msg.endswith('-- не найден.'), True)

        # print('--fail_file')
        source_df, msg = DataReader(
            self.path_to_file, 'fail_file.xlsx').read_data_from_stock_file(
            self.sheet_name, self.columns_letters_str)
        are_equal = df.equals(source_df)

        self.assertEqual(are_equal, False)
        self.assertEqual(msg.endswith('-- не найден.'), True)

        # print('--fail_columns')
        source_df, msg = DataReader(
            self.path_to_file, self.file_name).read_data_from_stock_file(
            self.sheet_name, 'fail_columns')
        are_equal = df.equals(source_df)

        self.assertEqual(are_equal, False)
        self.assertEqual(msg.startswith('ОШИБКА'), True)

        # print('--fail_sheet')
        source_df, msg = DataReader(
            self.path_to_file, self.file_name).read_data_from_stock_file(
            'fail_sheet', self.columns_letters_str)
        are_equal = df.equals(source_df)

        self.assertEqual(are_equal, False)
        self.assertEqual(msg.startswith('ОШИБКА'), True)

    def test_read_data_from_stock_file_by_openpyxl_success(self):
        # print('----- DataReader, test WB')
        # test_excel_column_names = data_dict_for_test_excel_file_1.keys()
        excel_file_column_names = DataReader(
            self.path_to_file, self.file_name).read_data_from_stock_file_by_openpyxl(
            self.sheet_name, ['A1', 'B1'])
        # self.assertEqual(list(self.test_excel_column_names), excel_file_column_names)
        self.assertEqual({'A1': 'Переход в Резервы', 'B1': 'Переход в СП плат'}, excel_file_column_names)

    def test_read_data_from_stock_file_by_openpyxl_none_cell(self):
        # print('----- DataReader, test none_cell')
        # test_excel_column_names = data_dict_for_test_excel_file_1.keys()
        excel_file_column_names = DataReader(
            self.path_to_file, self.file_name).read_data_from_stock_file_by_openpyxl(
            self.sheet_name, ['A1', 'F1'])
        # self.assertEqual(list(self.test_excel_column_names), excel_file_column_names)
        self.assertEqual({'A1': 'Переход в Резервы', 'F1': None}, excel_file_column_names)

    def test_read_data_from_stock_file_by_openpyxl_fail(self):
        # print('----- DataReader, test fail - incorrect list of cells')
        # test_excel_column_names = data_dict_for_test_excel_file_1.keys()
        excel_file_column_names = DataReader(
            self.path_to_file, self.file_name).read_data_from_stock_file_by_openpyxl(
            self.sheet_name, 'A1')
        # self.assertEqual(list(self.test_excel_column_names), excel_file_column_names)
        self.assertEqual(dict(), excel_file_column_names)


