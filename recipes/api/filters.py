import django_filters
from django.db.models import Count, Q

from recipes.models import Recipe


class CharAnyFilter(django_filters.BaseInFilter, django_filters.CharFilter):
    pass


class CharAllFilter(django_filters.BaseCSVFilter, django_filters.CharFilter):
    def filter(self, qs, value):
        if not value:
            return qs

        for item in value:
            qs = qs.filter(**{f"{self.field_name}__{self.lookup_expr}": item})

        return qs.distinct()


class EquipmentSubsetFilter(django_filters.BaseCSVFilter, django_filters.CharFilter):
    def filter(self, qs, value):
        if not value:
            return qs

        return qs.annotate(
            outside=Count("equipment", filter=~Q(equipment__equipment__in=value))
        ).filter(outside=0)


class RecipeFilter(django_filters.FilterSet):
    suche = django_filters.CharFilter(
        field_name="name",
        lookup_expr="icontains",
    )
    ernaehrung = CharAnyFilter(
        field_name="diets__diet",
        lookup_expr="in",
        distinct=True,
    )
    unvertraeglichkeit = CharAllFilter(
        field_name="intolerances__intolerance",
        lookup_expr="iexact",
    )
    mahlzeit = CharAnyFilter(
        field_name="meal_types__meal_type",
        lookup_expr="in",
        distinct=True,
    )
    eigenschaften = CharAllFilter(
        field_name="attributes__attribute",
        lookup_expr="iexact",
    )
    ausstattung = EquipmentSubsetFilter()

    class Meta:
        model = Recipe
        fields = (
            "suche",
            "ernaehrung",
            "unvertraeglichkeit",
            "mahlzeit",
            "eigenschaften",
            "ausstattung",
        )
