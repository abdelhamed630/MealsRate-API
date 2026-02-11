from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MealViewSet, OrderViewSet, ReviewViewSet, RegisterView
router = DefaultRouter()
router.register(r'meals', MealViewSet)
router.register(r'orders', OrderViewSet)
router.register(r'reviews', ReviewViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('register/', RegisterView.as_view(), name='register'),
]