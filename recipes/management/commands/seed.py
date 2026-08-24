"""Management command that fills the taxonomy tables with their fixed values.

Contents:
  * TAXONOMIES -- the models to seed, as (model, field name).
  * Command    -- the command itself, run with ``manage.py seed``.

The command is safe to run repeatedly: every entry is looked up first and only
created if it is missing, so existing recipes keep their assignments.
"""

from django.core.management.base import BaseCommand

from recipes.models import Attribute, Diet, Equipment, Intolerance, MealType

TAXONOMIES = [
    (Diet, "diet"),
    (Intolerance, "intolerance"),
    (MealType, "meal_type"),
    (Equipment, "equipment"),
    (Attribute, "attribute"),
]


class Command(BaseCommand):
    """Seeds the fixed classification values for recipes."""

    help = "Seeds diets, intolerances, meal types, equipment and attributes."

    def handle(self, *args, **options):
        """Create one row per choice value and report what was written."""
        for model, field_name in TAXONOMIES:
            field = model._meta.get_field(field_name)
            created_count = 0

            for value, _label in field.choices:
                _obj, created = model.objects.get_or_create(**{field_name: value})
                if created:
                    created_count += 1

            self.stdout.write(
                f"{model.__name__}: {created_count} new, {model.objects.count()} total"
            )

        self.stdout.write(self.style.SUCCESS("Done."))
