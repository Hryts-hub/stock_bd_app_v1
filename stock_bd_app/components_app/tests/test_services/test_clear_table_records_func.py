from django.test import TestCase
from components_app.services import clear_table_records
from components_app.models import StockFromExcel


class ServicesTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        # Create some records in the database
        StockFromExcel.objects.create(id=2)

    def test_clear_table_records(self):
        # print('----------Test clearing table records')

        # Call the function to clear records
        clear_table_records(StockFromExcel)

        # Check if all records were deleted
        self.assertEqual(StockFromExcel.objects.count(), 0)

