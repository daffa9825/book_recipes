from rest_framework import serializers
from .models import Recipe, FavoriteFoods
from django.contrib.auth import get_user_model
        
class RecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = '__all__'

class FavoriteFoodsSerializer(serializers.ModelSerializer):
    class Meta:
        model = FavoriteFoods
        fields = '__all__'