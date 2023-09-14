from django.core.management import BaseCommand
from components_app.services import clear_table_records
from django.apps import apps

# COMMAND

# python manage.py clear_table StockFromExcel


class Command(BaseCommand):
    help = 'Clears all records from a table'

    def add_arguments(self, parser):
        parser.add_argument('model_name', type=str, help='Name of the model to clear')

    def handle(self, *args, **options):
        model_name = options['model_name']
        try:
            model = apps.get_model('components_app', model_name)
        except LookupError:
            self.stdout.write(self.style.ERROR('Model not found'))
            return

        clear_table_records(model)
        self.stdout.write(self.style.SUCCESS(f'All records cleared for model {model_name}'))

