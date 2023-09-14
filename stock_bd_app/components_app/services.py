
from components_app.models import DEFAULT_NAN_VALUE
from tqdm import tqdm
import pandas as pd
import openpyxl
import io
import time
import psutil
from django.db import connection

import os
from dotenv import load_dotenv

load_dotenv()


# FUNCTIONS ------------------------------------------

def clear_table_records(model_class):
    model_class.objects.all().delete()

# CLASSES --------------------------------------------


class DataReader:
    def __init__(self, path_to_file, file_name):
        self.path_to_file = path_to_file
        self.file_name = file_name
        self.path = os.path.abspath(os.path.join(self.path_to_file, self.file_name))
        self.data = None
        self.msg = ''

    def read_data_from_stock_file(self, sheet_name, cols):
        # print('DataReader. File reading using pd.read_excel()')
        # print(self.path)
        if self.path_to_file is not None and os.path.exists(self.path):
            try:
                self.data = pd.read_excel(
                    self.path,
                    sheet_name=sheet_name,
                    usecols=cols,
                    engine='openpyxl',
                    dtype='object',
                    # This data type allows the columns to contain a mix of strings, numbers,
                    # and NaN values without any automatic type conversions
                )
            except Exception as e:
                self.msg = f'ОШИБКА: {type(e)}: {e}'
        else:
            self.msg = f'{self.path} -- не найден.'

        # print(self.data.shape)
        # print(self.data.dtypes)
        # print(self.msg)

        return self.data, self.msg

    def read_data_from_stock_file_by_openpyxl(self, sheet_name, cell_names):
        # print('DataReader. File reading using openpyxl.load_workbook() in read_only mode')
        # print(f'cell_names: {cell_names}')
        if self.path_to_file is not None and os.path.exists(self.path):
            try:
                # read-only mode optimized for faster performance
                # only interested in reading specific data
                # like column names and don't need to modify the workbook.

                # When you load an Excel file using openpyxl.load_workbook(file),
                # the file is not automatically closed.
                # You are responsible for explicitly closing it when you're done using it.
                # Failing to do so may lead to file locks or resource conflicts,
                # which could result in a PermissionError when trying to access the file later.

                # wb._archive.close() and wb.close() did not work in read_only mode
                # --> https://stackoverflow.com/questions/31416842/
                # /openpyxl-does-not-close-excel-workbook-in-read-only-mode

                # SOLUTION: Using a context manager ensures that the file is
                # properly closed when the block is exited.
                # The file is opened for binary reading because Excel files are binary files.

                with open(self.path, "rb") as f:
                    in_mem_file = io.BytesIO(f.read())
                    # file context stored in an in-memory binary stream using the io.BytesIO class

                wb = openpyxl.load_workbook(in_mem_file, read_only=True)
                sheet = wb[sheet_name]
                excel_file_column_names = {
                    cell_name: sheet[cell_name].value for cell_name in cell_names
                }
            except Exception as e:
                excel_file_column_names = dict()
                print(f'ОШИБКА: {type(e)}: {e}')
            return excel_file_column_names


# -------------------- functions

# this func will be replaced by updated one.
# table should be filled from the source tables
# def create_stock_components():
#     # read stock file --> df_stock_components
#     cols = 'C, D, E, F, G'
#     sheet_name = 'Склад'
#     df_stock_components, msg = DataReader(
#         PATH_TO_FILE_STOCK, FILE_STOCK).read_data_from_stock_file(sheet_name, cols)
#
#     # print(df_stock_components.shape)
#     # print(df_stock_components.dtypes)
#
#     df_stock_components = df_stock_components.dropna(subset=['Артикул'])
#     df_stock_components = df_stock_components.astype({'Артикул': int})
#     # df_stock_components = df_stock_components.iloc[12:17]
#
#     created_count = 0
#     err_count = 0
#
#     # fill DB by df
#     for raw in tqdm(df_stock_components.itertuples(index=False)):  # index=False
#         try:
#             # print(raw)
#             # print(raw[0])
#             # print(raw[1])
#             # print(raw[4])
#             StockComponents.objects.create(
#                 art_number=raw[0],
#                 component_stock_naming=raw[4],
#                 category=raw[1],
#                 type=raw[2],
#                 subtype=raw[3],
#                 user=CustomUser.objects.get(username='hryts')  # 'hryts'
#             )
#             created_count += 1
#         except Exception as e:
#             print(e)
#             print(raw)
#             err_count += 1
#             pass
#
#     print(f'created_count = {created_count}, err_count = {err_count}')
#
#     pass


class StockTabFromExcelUpdater:
    def __init__(self, model, path_to_file, file_name, sheet_name, columns):
        self.model = model
        self.path_to_file = path_to_file
        self.file_name = file_name
        self.table_name = model._meta.db_table
        self.db_column_names = {
            field.name: field.verbose_name for field in self.model._meta.get_fields()
        }
        self.db_verbose_names = {
            field.verbose_name: field.name for field in self.model._meta.get_fields()
        }
        self.sheet_name = sheet_name
        self.columns = columns  # "A, B, C..."

        # read not all cols from file, but just self.columns using cell_names
        self.column_names_from_excel_file = DataReader(
            self.path_to_file, self.file_name
        ).read_data_from_stock_file_by_openpyxl(self.sheet_name, self.make_cell_names(self.columns))

        self.col_list = [
            k for k, v in self.db_column_names.items() if v in self.column_names_from_excel_file.values()
        ]

        self.nan_value = DEFAULT_NAN_VALUE
        self.offset = 2  # offset for indexes is manually set to correspond art_numbers

    @staticmethod
    def make_cell_names(columns):
        columns_list = columns.split(', ')
        cell_names = [f'{column_letter}1' for column_letter in columns_list]
        return cell_names

    def validate_columns(self):
        """
        Checks that excel_file_col_names (input cols for create-update, not all cols) IN DB_col_names
        If NOT -->> flag is False -->> need to alter table
        :return: flag
        """

        flag = True

        if self.column_names_from_excel_file:
            for cell, col in self.column_names_from_excel_file.items():
                if col not in self.db_column_names.values():
                    flag = False
                    print(f'ERR-CELL is << {cell} >> (column_name of this cell not found in DB): {col}')
        else:
            flag = False
        print(flag)
        return flag

    def read_specified_columns_from_db_table(self):
        """
        Reads data from DB-table.
        Col_names filtered using verbose names of DB-columns,
        and index-numerating corrected with offset
        to get DF with the same structure as df_from_excel_file,
        and indexes that can be used in comparison of two DFs
        :return: DF
        """

        # print(f'self.db_column_names.items() = {self.db_column_names.items()}')
        # print(f'self.column_names_from_excel_file = {self.column_names_from_excel_file}')
        # print(f'self.column_names_from_excel_file.values() = {self.column_names_from_excel_file.values()}')

        columns_str = ', '.join(self.col_list)
        # print(f'columns_str = {columns_str}')
        with connection.cursor() as cursor:
            query = f"SELECT {columns_str} FROM {self.table_name};"
            cursor.execute(query)
            data = cursor.fetchall()

        db_df = pd.DataFrame(data, columns=self.column_names_from_excel_file.values())
        db_df.index = db_df.index + self.offset

        # col_list = [k for k, v in self.db_column_names.items() if v in self.column_names_from_excel_file]
        # queryset = self.model.objects.values(*col_list)
        # db_df = pd.DataFrame.from_records(queryset, index='id', columns=self.column_names_from_excel_file)

        # print(db_df.shape)
        # print(db_df.dtypes)
        # print('DB HEAD')
        # print(db_df.head())
        # print('TAIL')
        # print(db_df.tail())
        return db_df

    def read_specified_columns_from_excel_sheet(self, db_art_max):
        """
        Reads data from excel_file by DataReader class.
        Index-numerating corrected with offset,
        empty-tail of DF discarded using art_number_max,
        None values filled with default nan_value of str type,
        all values in DF converted to STR type.
        :return: DF
        """

        source_df, msg = DataReader(
            self.path_to_file, self.file_name).read_data_from_stock_file(
            self.sheet_name, self.columns)

        source_df.index = source_df.index + self.offset

        # print(f'1 db_art_max in func = {db_art_max}')
        # print(f'2 db_art_max in func = {db_art_max}')
        # print(f'type(db_art_max) = {type(db_art_max)}')

        # if some last art_numbers were deleted from file - this changes update in DB by default nan_value
        art_number_max = max(source_df['Артикул'].max(), db_art_max)
        # print(f'art_number_max = {art_number_max}')
        source_df = source_df[:(art_number_max-1)]

        # all values in columns (except index) should be str - and nan_value is str type
        source_df = source_df.fillna(self.nan_value)

        # print(f'self.column_names_from_excel_file = {self.column_names_from_excel_file}')

        type_dict = {col: str for col in self.column_names_from_excel_file.values()}
        source_df = source_df.astype(type_dict)

        # print(source_df.shape)
        # print(source_df.dtypes)
        # print('HEAD - after astype')
        # print(source_df.head())
        # print('TAIL')
        # print(source_df.tail())
        return source_df

    def validate_df_to_get_unequal_rows(self):
        if self.validate_columns():
            db_df = self.read_specified_columns_from_db_table()
            db_art_max = db_df.index.max()
            source_df = self.read_specified_columns_from_excel_sheet(db_art_max)

            # unequal_indexes is an array containing the indexes
            # that are differs between the two DataFrames.
            if not source_df.empty and not db_df.empty:
                unequal_indexes = source_df.index[~source_df.index.isin(db_df.index)].tolist()
            else:
                unequal_indexes = []

            # new rows are created first, then unequal rows are updated
            if unequal_indexes:
                return source_df.loc[unequal_indexes]
            elif db_df.empty or source_df.empty:
                return source_df
            else:
                # can't compare None (None --> default nan value = ''
                comparison_result = db_df == source_df
                unequal_rows = source_df[~comparison_result.all(axis=1)]

                return unequal_rows

    def create_by_iterrows(self, df):
        created_count = 0
        err_count = 0

        start_time = time.time()
        mem_before = psutil.virtual_memory().used
        # col names in df are verbose names for table in db
        for index, row in tqdm(df.iterrows(), total=len(df)):
            columns = {
                self.db_verbose_names[col_name]: value for col_name, value in row.items()
            }
            try:
                self.model.objects.create(
                    id=index,
                    **columns
                )
                created_count += 1

            except Exception as e:
                err_count += 1
                pass

        end_time = time.time()
        mem_after = psutil.virtual_memory().used
        print("DONE !!!")
        print("Time for iterrows():", end_time - start_time, "seconds")
        print("Memory used by iterrows():", mem_after - mem_before, "bytes")
        print(f'created_count = {created_count}, err_count = {err_count}')
        return created_count, err_count

    def update_by_iterrows(self, df):
        updated_count = 0
        err_count = 0

        start_time = time.time()
        mem_before = psutil.virtual_memory().used
        # col names in df are verbose names for table in db
        for index, row in tqdm(df.iterrows(), total=len(df)):
            columns = {
                self.db_verbose_names[col_name]: value for col_name, value in row.items()
            }
            try:
                # unique_identifier = index
                obj = self.model.objects.get(id=index)

                for col, value in columns.items():
                    setattr(obj, col, value)  # Dynamically set the attribute
                obj.save()  # Save the changes to the object
                updated_count += 1

            except Exception as e:
                # print(e)
                err_count += 1
                pass

        end_time = time.time()
        mem_after = psutil.virtual_memory().used
        print("DONE !!!")
        print("Time for iterrows():", end_time - start_time, "seconds")
        print("Memory used by iterrows():", mem_after - mem_before, "bytes")
        print(f'updated_count = {updated_count}, err_count = {err_count}')
        return updated_count, err_count

    def update_and_create_by_iterrows(self):
        df = self.validate_df_to_get_unequal_rows()
        if df is not None:
            created_count, err_count_create = self.create_by_iterrows(df)
            df = self.validate_df_to_get_unequal_rows()
            updated_count, err_count_update = self.update_by_iterrows(df)
            return created_count, err_count_create, updated_count, err_count_update
        else:
            print('CHECK ERRORS!!! BD not updated!')
            return 0, 0, 0, 0

    # -----------------------
    def create_by_itertuples(self, df):
        created_count = 0
        err_count = 0

        start_time = time.time()
        mem_before = psutil.virtual_memory().used

        len_df = len(df)
        if len_df > 0:

            for row in tqdm(df.itertuples(), total=len_df):
                # col names in df are verbose names for table in db
                columns = {
                    self.col_list[i]: row[i+1] for i in range(0, len(self.col_list))
                }

                try:
                    # obj - for manual testing to look at obj's properties obj.art_number, ...
                    obj = self.model.objects.create(
                        id=row[0],
                        **columns,
                    )

                    created_count += 1

                except Exception as e:
                    # if err_count < 5:
                    #     print(row)
                    #     print(e)
                    err_count += 1
                    pass

        end_time = time.time()
        mem_after = psutil.virtual_memory().used
        print("DONE !!!")
        print("Time for itertuples():", end_time - start_time, "seconds")
        print("Memory used by itertuples():", mem_after - mem_before, "bytes")
        print(f'created_count = {created_count}, err_count = {err_count}')
        return created_count, err_count

    def update_by_itertuples(self, df):
        updated_count = 0
        err_count = 0

        start_time = time.time()
        mem_before = psutil.virtual_memory().used

        len_df = len(df)
        if len_df > 0:

            for row in tqdm(df.itertuples(), total=len_df):
                # col names in df are verbose names for table in db
                columns = {
                    self.col_list[i]: row[i+1] for i in range(0, len(self.col_list))
                }
                try:
                    obj = self.model.objects.get(id=row[0])
                    for col, value in columns.items():
                        setattr(obj, col, value)  # Dynamically set the attribute

                    obj.save()  # Save the changes to the object
                    updated_count += 1

                except Exception as e:
                    # print(e)
                    err_count += 1
                    pass

        end_time = time.time()
        mem_after = psutil.virtual_memory().used
        print("DONE !!!")
        print("Time for itertuples():", end_time - start_time, "seconds")
        print("Memory used by itertuples():", mem_after - mem_before, "bytes")
        print(f'updated_count = {updated_count}, err_count = {err_count}')
        return updated_count, err_count

    def update_and_create_by_itertuples(self):
        df = self.validate_df_to_get_unequal_rows()
        if df is not None:
            created_count, err_count_create = self.create_by_itertuples(df)
            df = self.validate_df_to_get_unequal_rows()
            updated_count, err_count_update = self.update_by_itertuples(df)
            return created_count, err_count_create, updated_count, err_count_update
        else:
            print('CHECK ERRORS!!! BD not updated!')
            return 0, 0, 0, 0

    # When using iterrows(), NaN values are preserved in the resulting named tuple
    # When using itertuples(), NaN values are converted to str 'nan' (lowercase)
    # in the resulting named tuple. This is a pandas-specific NaN representation.

