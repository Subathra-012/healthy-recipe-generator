from rest_framework import generics, viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import get_user_model

from .models import MealPlan, Favorite, PantryItem, Budget, GroceryList
from .serializers import (
    RegisterSerializer, 
    UserSerializer, 
    MealPlanSerializer, 
    FavoriteSerializer,
    PantryItemSerializer,
    BudgetSerializer,
    GroceryListSerializer
)

User = get_user_model()

# ---------------------------------------------------------
# AUTHENTICATION
# ---------------------------------------------------------

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (permissions.AllowAny,)
    serializer_class = RegisterSerializer

class CustomLoginView(TokenObtainPairView):
    # Uses default simplejwt filtering, can be customized
    pass

# ---------------------------------------------------------
# MEAL PLANS & HISTORY
# ---------------------------------------------------------

class MealPlanViewSet(viewsets.ModelViewSet):
    serializer_class = MealPlanSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Return only plans for the current user
        return MealPlan.objects.filter(user=self.request.user).order_by('-created_at')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['get'])
    def recent(self, request):
        """
        Return the last 5 generated plans.
        """
        recent_plans = self.get_queryset()[:5]
        serializer = self.get_serializer(recent_plans, many=True)
        return Response(serializer.data)

# ---------------------------------------------------------
# FAVORITES
# ---------------------------------------------------------

class FavoriteViewSet(viewsets.ModelViewSet):
    serializer_class = FavoriteSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Favorite.objects.filter(user=self.request.user).order_by('-saved_at')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


# ---------------------------------------------------------
# PANTRY MANAGEMENT
# ---------------------------------------------------------

class PantryItemViewSet(viewsets.ModelViewSet):
    serializer_class = PantryItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return PantryItem.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


# ---------------------------------------------------------
# BUDGET
# ---------------------------------------------------------

class BudgetViewSet(viewsets.ModelViewSet):
    serializer_class = BudgetSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Budget.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


# ---------------------------------------------------------
# GROCERY LISTS
# ---------------------------------------------------------

class GroceryListViewSet(viewsets.ModelViewSet):
    serializer_class = GroceryListSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return GroceryList.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
