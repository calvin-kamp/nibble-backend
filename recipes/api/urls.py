from rest_framework import routers

from .views import RecipeViewSet

router = routers.SimpleRouter()
router.register(r"", RecipeViewSet, basename="recipe")

urlpatterns = router.urls
