from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import CategoryViewSet, TicketViewSet, ticket_stats

router = DefaultRouter()
router.register('categories', CategoryViewSet, basename='category')
router.register('tickets', TicketViewSet, basename='ticket')

urlpatterns = [
    path('tickets/stats/', ticket_stats, name='ticket-stats'),
] + router.urls