from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets

from common.permissions import IsAdminOrReadOnly

from .models import Category
from .serializers import CategorySerializer


class CategoryViewSet(viewsets.ModelViewSet):
    """
    GET    /api/categories/
    POST   /api/categories/
    GET    /api/categories/{id}/
    PATCH  /api/categories/{id}/
    DELETE /api/categories/{id}/
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]