from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.permissions import AllowAny

from recipes.models import Recipe

from .filters import RecipeFilter
from .serializers import RecipeDetailSerializer, RecipeListSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend]
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.action == "list":
            return RecipeListSerializer

        return RecipeDetailSerializer
