from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    RegisterView, CustomLoginView, MealPlanViewSet, FavoriteViewSet,
    PantryItemViewSet, BudgetViewSet, GroceryListViewSet
)

router = DefaultRouter()
router.register(r'meal-plans', MealPlanViewSet, basename='mealplan')
router.register(r'favorites', FavoriteViewSet, basename='favorite')
router.register(r'pantry', PantryItemViewSet, basename='pantryitem')
router.register(r'budget', BudgetViewSet, basename='budget')
router.register(r'grocery-lists', GroceryListViewSet, basename='grocerylist')

urlpatterns = [
    # Auth
    path('auth/register/', RegisterView.as_view(), name='auth_register'),
    path('auth/login/', CustomLoginView.as_view(), name='auth_login'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # API Routes (History, Favorites, Save)
    path('', include(router.urls)),
]
