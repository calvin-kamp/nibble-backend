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
    diets = serializers.StringRelatedField(many=True)
    intolerances = serializers.StringRelatedField(many=True)
    meal_types = serializers.StringRelatedField(many=True)
    equipment = serializers.StringRelatedField(many=True)
    attributes = serializers.StringRelatedField(many=True)

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

    diets = serializers.PrimaryKeyRelatedField(
        required=False,
        many=True,
        queryset=Diet.objects.all(),
        write_only=True,
    )
    intolerances = serializers.PrimaryKeyRelatedField(
        required=False,
        many=True,
        queryset=Intolerance.objects.all(),
        write_only=True,
    )
    meal_types = serializers.PrimaryKeyRelatedField(
        required=False,
        many=True,
        queryset=MealType.objects.all(),
        write_only=True,
    )
    equipment = serializers.PrimaryKeyRelatedField(
        required=False,
        many=True,
        queryset=Equipment.objects.all(),
        write_only=True,
    )
    attributes = serializers.PrimaryKeyRelatedField(
        required=False,
        many=True,
        queryset=Attribute.objects.all(),
        write_only=True,
    )

    diet_labels = serializers.StringRelatedField(
        many=True,
        source="diets",
        read_only=True,
    )
    intolerance_labels = serializers.StringRelatedField(
        many=True,
        source="intolerances",
        read_only=True,
    )
    meal_type_labels = serializers.StringRelatedField(
        many=True,
        source="meal_types",
        read_only=True,
    )
    equipment_labels = serializers.StringRelatedField(
        many=True,
        source="equipment",
        read_only=True,
    )
    attribute_labels = serializers.StringRelatedField(
        many=True,
        source="attributes",
        read_only=True,
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
            "diet_labels",
            "intolerance_labels",
            "meal_type_labels",
            "equipment_labels",
            "attribute_labels",
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
