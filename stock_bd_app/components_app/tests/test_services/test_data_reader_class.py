import pandas as pd
from django.test import TestCase

from components_app.management.commands.update_table_from_excel import FILE_STOCK, SHEET_NAME
from components_app.services import DataReader
import os
import openpyxl
from openpyxl.comments import Comment

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

TEST_COLUMNS = 'C, D'

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
    columns_letters_str = TEST_COLUMNS

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.dataframe_for_excel_file.to_excel(
            cls.full_path,
            sheet_name=cls.sheet_name,
            na_rep='',
            index=False,
            startrow=0,
            engine='openpyxl',
        )

        wb = openpyxl.load_workbook(cls.full_path)
        sheet = wb[cls.sheet_name]

        comment1 = Comment("This is a comment for cell C2", "Author 1")
        sheet['C2'].comment = comment1

        comment2 = Comment("Another comment for cell C3", "Author 2")
        sheet['C3'].comment = comment2
        wb.save(cls.full_path)

        wb.close()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()

        # Clean up by deleting the test Excel file
        if os.path.exists(cls.full_path):
            os.remove(cls.full_path)

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
        df = pd.read_excel(
                    self.full_path,
                    sheet_name=self.sheet_name,
                    usecols=self.columns_letters_str,
                    engine='openpyxl',
                    dtype='object',
                )
        source_df, msg = DataReader(
            self.path_to_file, self.file_name).read_data_from_stock_file(
            self.sheet_name, self.columns_letters_str)
        are_equal = df.equals(source_df)

        self.assertEqual(are_equal, True)
        self.assertEqual(msg, '')

    def test_read_excel_to_dataframe_fail(self):
        df = pd.read_excel(
                    self.full_path,
                    sheet_name=self.sheet_name,
                    usecols=self.columns_letters_str,
                    engine='openpyxl',
                    dtype='object',
                )

        source_df, msg = DataReader(
            'fail_path/', self.file_name).read_data_from_stock_file(
            self.sheet_name, self.columns_letters_str)
        are_equal = df.equals(source_df)

        self.assertEqual(are_equal, False)
        self.assertEqual(msg.endswith('-- not found.'), True)

        source_df, msg = DataReader(
            self.path_to_file, 'fail_file.xlsx').read_data_from_stock_file(
            self.sheet_name, self.columns_letters_str)
        are_equal = df.equals(source_df)

        self.assertEqual(are_equal, False)
        self.assertEqual(msg.endswith('-- not found.'), True)

        source_df, msg = DataReader(
            self.path_to_file, self.file_name).read_data_from_stock_file(
            self.sheet_name, 'fail_columns')
        are_equal = df.equals(source_df)

        self.assertEqual(are_equal, False)
        self.assertEqual(msg.startswith('ERROR'), True)

        source_df, msg = DataReader(
            self.path_to_file, self.file_name).read_data_from_stock_file(
            'fail_sheet', self.columns_letters_str)
        are_equal = df.equals(source_df)

        self.assertEqual(are_equal, False)
        self.assertEqual(msg.startswith('ERROR'), True)

    def test_read_data_from_stock_file_by_openpyxl_success(self):
        excel_file_column_names = DataReader(
            self.path_to_file, self.file_name).read_data_from_stock_file_by_openpyxl(
            self.sheet_name, ['A1', 'B1'])
        self.assertEqual({'A1': 'Переход в Резервы', 'B1': 'Переход в СП плат'}, excel_file_column_names)

    def test_read_data_from_stock_file_by_openpyxl_none_cell(self):
        excel_file_column_names = DataReader(
            self.path_to_file, self.file_name).read_data_from_stock_file_by_openpyxl(
            self.sheet_name, ['A1', 'F1'])
        self.assertEqual({'A1': 'Переход в Резервы', 'F1': None}, excel_file_column_names)

    def test_read_data_from_stock_file_by_openpyxl_fail(self):
        excel_file_column_names = DataReader(
            self.path_to_file, self.file_name).read_data_from_stock_file_by_openpyxl(
            self.sheet_name, 'A1')
        self.assertEqual(dict(), excel_file_column_names)

    def test_read_comments_from_stock_file_by_openpyxl_1(self):
        # test col where no comments
        comment_dict = DataReader(
            self.path_to_file, self.file_name).read_comments_from_stock_file_by_openpyxl(
            self.sheet_name, {'A1': ['A2', 'A3', 'A4', 'A5', 'A6']})
        self.assertEqual({'Переход в Резервы': [None for _ in range(5)]}, comment_dict)

    def test_read_comments_from_stock_file_by_openpyxl_2(self):
        # test col with 2 comments
        comment_dict = DataReader(
            self.path_to_file, self.file_name).read_comments_from_stock_file_by_openpyxl(
            self.sheet_name, {'C1': ['C2', 'C3', 'C4', 'C5', 'C6']})
        self.assertEqual({
            'Артикул': [
                "This is a comment for cell C2",
                "Another comment for cell C3",
                None,
                None,
                None,
            ]
        }, comment_dict)
