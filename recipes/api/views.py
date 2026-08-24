from rest_framework import viewsets
from rest_framework.permissions import AllowAny

from recipes.models import Recipe

from .serializers import RecipeDetailSerializer, RecipeListSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = [AllowAny]

    def get_queryset(self):
        queryset = Recipe.objects.all()

        return queryset

    def get_serializer_class(self):
        if self.action == "list":
            return RecipeListSerializer

        return RecipeDetailSerializer
