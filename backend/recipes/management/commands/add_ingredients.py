import json

from django.core.management import BaseCommand

from backend.settings import BASE_DIR
from recipes.models import Ingredient


class Command(BaseCommand):
    def handle(self, *args, **options):
        with open(BASE_DIR / 'data' / 'ingredients.json', 'rb') as file:
            ingredients = json.load(file)
            for ingredient in ingredients:
                Ingredient.objects.create(name=ingredient['name'],
                                          measurement_unit=ingredient[
                                              'measurement_unit'])
