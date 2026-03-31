from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import MealPlan, Favorite, PantryItem, Budget, GroceryList

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email')

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password')

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user

class MealPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = MealPlan
        fields = '__all__'
        read_only_fields = ('user', 'created_at')

class FavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favorite
        fields = '__all__'
        read_only_fields = ('user', 'saved_at')

class PantryItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = PantryItem
        fields = '__all__'
        read_only_fields = ('user', 'updated_at')

class BudgetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Budget
        fields = '__all__'
        read_only_fields = ('user', 'created_at', 'updated_at')

class GroceryListSerializer(serializers.ModelSerializer):
    class Meta:
        model = GroceryList
        fields = '__all__'
        read_only_fields = ('user', 'created_at')
