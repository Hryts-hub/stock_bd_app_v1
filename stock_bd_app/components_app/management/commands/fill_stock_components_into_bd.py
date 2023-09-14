from django.core.management import BaseCommand
from components_app.services import create_stock_components


class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        create_stock_components()

