from django.utils.text import slugify
from rest_framework import serializers

from recipes.models import (
    Attribute,
    CookingStep,
    Diet,
    Equipment,
    Ingredient,
    Intolerance,
    MealType,
    Recipe,
    RecipeIngredient,
)


class ChoiceSlugRelatedField(serializers.SlugRelatedField):
    def to_representation(self, obj):
        return getattr(obj, f"get_{self.slug_field}_display")()


class CookingStepSerializer(serializers.ModelSerializer):
    class Meta:
        model = CookingStep
        fields = ("step", "text")


class RecipeIngredientSerializer(serializers.ModelSerializer):
    unit_label = serializers.CharField(
        source="get_unit_display",
        read_only=True,
    )

    ingredient = serializers.CharField(write_only=True)
    ingredient_name = serializers.CharField(
        source="ingredient.name",
        read_only=True,
    )

    class Meta:
        model = RecipeIngredient
        fields = (
            "amount",
            "unit",
            "unit_label",
            "ingredient",
            "ingredient_name",
        )
        extra_kwargs = {
            "unit": {
                "write_only": True,
            }
        }


class RecipeListSerializer(serializers.ModelSerializer):
    diets = ChoiceSlugRelatedField(
        slug_field="diet",
        many=True,
        read_only=True,
    )
    intolerances = ChoiceSlugRelatedField(
        slug_field="intolerance",
        many=True,
        read_only=True,
    )
    meal_types = ChoiceSlugRelatedField(
        slug_field="meal_type",
        many=True,
        read_only=True,
    )
    equipment = ChoiceSlugRelatedField(
        slug_field="equipment",
        many=True,
        read_only=True,
    )
    attributes = ChoiceSlugRelatedField(
        slug_field="attribute",
        many=True,
        read_only=True,
    )

    class Meta:
        model = Recipe
        fields = (
            "id",
            "image",
            "name",
            "duration_minutes",
            "diets",
            "intolerances",
            "meal_types",
            "equipment",
            "attributes",
            "kcal_per_serving",
            "created_at",
        )


class RecipeDetailSerializer(serializers.ModelSerializer):
    slug = serializers.SerializerMethodField()

    ingredients = RecipeIngredientSerializer(many=True)
    cooking_steps = CookingStepSerializer(many=True)

    diets = ChoiceSlugRelatedField(
        slug_field="diet",
        queryset=Diet.objects.all(),
        many=True,
        required=False,
    )
    intolerances = ChoiceSlugRelatedField(
        slug_field="intolerance",
        queryset=Intolerance.objects.all(),
        many=True,
        required=False,
    )
    meal_types = ChoiceSlugRelatedField(
        slug_field="meal_type",
        queryset=MealType.objects.all(),
        many=True,
        required=False,
    )
    equipment = ChoiceSlugRelatedField(
        slug_field="equipment",
        queryset=Equipment.objects.all(),
        many=True,
        required=False,
    )
    attributes = ChoiceSlugRelatedField(
        slug_field="attribute",
        queryset=Attribute.objects.all(),
        many=True,
        required=False,
    )

    class Meta:
        model = Recipe
        fields = (
            "id",
            "image",
            "slug",
            "name",
            "description",
            "ingredients",
            "cooking_steps",
            "protein_per_serving",
            "carbs_per_serving",
            "fat_per_serving",
            "kcal_per_serving",
            "servings",
            "duration_minutes",
            "diets",
            "intolerances",
            "meal_types",
            "equipment",
            "attributes",
            "updated_at",
            "created_at",
        )

    def get_slug(self, obj):
        name = obj.name
        name = name.replace("ä", "ae").replace("Ä", "Ae")
        name = name.replace("ö", "oe").replace("Ö", "Oe")
        name = name.replace("ü", "ue").replace("Ü", "Ue")
        name = name.replace("ß", "ss")

        slugified_name = slugify(name)

        return f"{obj.id}-{slugified_name}"

    def create(self, validated_data):
        ingredients_data = validated_data.pop("ingredients")
        cooking_steps_data = validated_data.pop("cooking_steps")

        diets_data = validated_data.pop("diets", [])
        intolerances_data = validated_data.pop("intolerances", [])
        meal_types_data = validated_data.pop("meal_types", [])
        equipment_data = validated_data.pop("equipment", [])
        attributes_data = validated_data.pop("attributes", [])

        recipe = Recipe.objects.create(**validated_data)

        for ingredient in ingredients_data:
            ingredient_name = ingredient.pop("ingredient")
            ingredient_obj, _created = Ingredient.objects.get_or_create(
                name=ingredient_name
            )

            RecipeIngredient.objects.create(
                recipe=recipe,
                ingredient=ingredient_obj,
                **ingredient,
            )

        for cooking_step in cooking_steps_data:
            CookingStep.objects.create(recipe=recipe, **cooking_step)

        recipe.diets.set(diets_data)
        recipe.intolerances.set(intolerances_data)
        recipe.meal_types.set(meal_types_data)
        recipe.equipment.set(equipment_data)
        recipe.attributes.set(attributes_data)

        return recipe
