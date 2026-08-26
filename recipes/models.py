from django.core.validators import MinValueValidator
from django.db import models


# Create your models here.
class Ingredient(models.Model):
    name = models.CharField(
        max_length=60,
        unique=True,
    )

    def __str__(self):
        return self.name


class Diet(models.Model):
    class DietChoice(models.TextChoices):
        VEGAN = "vegan", "Vegan"
        VEGETARISCH = "vegetarisch", "Vegetarisch"
        PESCETARISCH = "pescetarisch", "Pescetarisch"

    diet = models.CharField(
        choices=DietChoice,
        max_length=12,
        unique=True,
    )

    def __str__(self):
        return self.get_diet_display()


class Intolerance(models.Model):
    class IntoleranceChoice(models.TextChoices):
        GLUTENFREI = "glutenfrei", "Glutenfrei"
        LAKTOSEFREI = "laktosefrei", "Laktosefrei"

    intolerance = models.CharField(
        choices=IntoleranceChoice,
        max_length=11,
        unique=True,
    )

    def __str__(self):
        return self.get_intolerance_display()


class MealType(models.Model):
    class MealTypeChoice(models.TextChoices):
        FRUEHSTUECK = "fruehstueck", "Frühstück"
        MITTAGESSEN = "mittagessen", "Mittagessen"
        ABENDESSEN = "abendessen", "Abendessen"

        SNACK = "snack", "Snack"
        DESSERT = "dessert", "Dessert"

    meal_type = models.CharField(
        choices=MealTypeChoice,
        max_length=11,
        unique=True,
    )

    def __str__(self):
        return self.get_meal_type_display()


class Equipment(models.Model):
    class EquipmentChoice(models.TextChoices):
        BACKOFEN = "backofen", "Backofen"
        HERD = "herd", "Herd"
        AIRFRYER = "airfryer", "Airfryer"
        MIXER = "mixer", "Mixer"
        OHNE_KOCHEN = "ohne-kochen", "Ohne Kochen"

    equipment = models.CharField(
        choices=EquipmentChoice,
        max_length=11,
        unique=True,
    )

    def __str__(self):
        return self.get_equipment_display()


class Attribute(models.Model):
    class AttributeChoice(models.TextChoices):
        PROTEINREICH = "proteinreich", "Proteinreich"
        KALORIENARM = "kalorienarm", "Kalorienarm"
        MEAL_PREP = "meal-prep", "Meal Prep"
        UNTER_30_MIN = "unter-30-min", "Unter 30 Min"
        WENIG_ZUTATEN = "wenig-zutaten", "Wenig Zutaten"

    attribute = models.CharField(
        choices=AttributeChoice,
        max_length=13,
        unique=True,
    )

    def __str__(self):
        return self.get_attribute_display()


class Recipe(models.Model):
    image = models.ImageField(
        upload_to="rezepte/",
        blank=True,
    )

    name = models.CharField(max_length=120)
    description = models.TextField(
        max_length=500,
        blank=True,
    )

    protein_per_serving = models.IntegerField(validators=[MinValueValidator(0)])
    carbs_per_serving = models.IntegerField(validators=[MinValueValidator(0)])
    fat_per_serving = models.IntegerField(validators=[MinValueValidator(0)])
    kcal_per_serving = models.IntegerField(validators=[MinValueValidator(0)])

    servings = models.PositiveIntegerField()
    duration_minutes = models.PositiveIntegerField()

    diets = models.ManyToManyField(Diet, blank=True)
    intolerances = models.ManyToManyField(Intolerance, blank=True)
    meal_types = models.ManyToManyField(MealType, blank=True)
    equipment = models.ManyToManyField(Equipment, blank=True)
    attributes = models.ManyToManyField(Attribute, blank=True)

    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    class UnitChoice(models.IntegerChoices):
        G = 10, "g"
        KG = 11, "kg"

        ML = 20, "ml"
        L = 21, "l"

        TL = 30, "TL"
        EL = 31, "EL"
        PRISE = 32, "Prise"

        STUECK = 40, "Stück"
        ZEHE = 41, "Zehe"
        BUND = 42, "Bund"
        SCHEIBE = 43, "Scheibe"
        DOSE = 44, "Dose"
        PACKUNG = 45, "Packung"

    amount = models.DecimalField(
        decimal_places=1,
        max_digits=5,
        validators=[MinValueValidator(0)],
    )
    unit = models.IntegerField(choices=UnitChoice)
    recipe = models.ForeignKey(
        Recipe,
        related_name="ingredients",
        on_delete=models.CASCADE,
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return self.ingredient.name


class CookingStep(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="cooking_steps",
    )
    text = models.TextField(max_length=500)
    step = models.PositiveIntegerField()

    class Meta:
        ordering = ["step"]

    def __str__(self):
        return f"{self.step}. {self.text}"
