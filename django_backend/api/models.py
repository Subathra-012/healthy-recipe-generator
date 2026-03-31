from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid

class User(AbstractUser):
    """
    Custom User model to allow for future extensions (e.g., bio, avatar).
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email

class MealPlan(models.Model):
    """
    Stores generated weekly meal plans for a user.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='meal_plans')
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Stores the full 7-day schedule (JSON)
    plan_data = models.JSONField() 
    
    # Stores the nutrition summary (BMR, TDEE, etc.)
    nutrition_summary = models.JSONField(default=dict)
    
    # Stores the grocery list
    grocery_list = models.JSONField(default=dict)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Plan {self.id} for {self.user.email} at {self.created_at}"

class Favorite(models.Model):
    """
    Stores user's favorite recipes or plans.
    """
    ITEM_TYPES = (
        ('RECIPE', 'Recipe'),
        ('PLAN', 'Meal Plan'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites')
    item_type = models.CharField(max_length=10, choices=ITEM_TYPES, default='RECIPE')
    
    # Stores the content of the favorite item (Title, Ingredients, etc.)
    item_data = models.JSONField()
    
    saved_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-saved_at']

    def __str__(self):
        return f"{self.get_item_type_display()} saved by {self.user.email}"


class PantryItem(models.Model):
    """Tracks ingredients the user has in their pantry."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='pantry_items')
    ingredient_name = models.CharField(max_length=200)
    quantity = models.FloatField(default=1.0)
    unit = models.CharField(max_length=50, default='piece')
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['ingredient_name']
        unique_together = ['user', 'ingredient_name']

    def __str__(self):
        return f"{self.ingredient_name} ({self.quantity} {self.unit})"


class Budget(models.Model):
    """Weekly grocery budget for a user."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='grocery_budget')
    weekly_amount = models.FloatField(default=0)
    currency = models.CharField(max_length=10, default='INR')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Budget: {self.currency} {self.weekly_amount} for {self.user.email}"


class GroceryList(models.Model):
    """Stores optimized grocery lists linked to meal plans."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='grocery_lists')
    meal_plan = models.ForeignKey(MealPlan, on_delete=models.SET_NULL, null=True, blank=True, related_name='optimized_lists')
    optimized_data = models.JSONField(default=dict)
    total_cost = models.FloatField(default=0)
    currency = models.CharField(max_length=10, default='INR')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Grocery List {self.id} - {self.currency} {self.total_cost}"
