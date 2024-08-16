from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from .views import CategoryList, LevelList, LoginUser, SignupUser, RecipeUpdateIsFavorite, MyFavoriteRecipe, MyRecipe, DetailRecipe, RecipeView

urlpatterns = [
    path("user-management/users/sign-up", SignupUser.as_view()),
    path("user-management/users/sign-in", LoginUser.as_view()),
    path('token', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh', TokenRefreshView.as_view(), name='token_refresh'),
    path('book-recipe/book-recipes/', RecipeView.as_view()),
    path('book-recipe/book-recipes/<int:id>/favorites', RecipeUpdateIsFavorite.as_view()),
    path('book-recipe-masters/category-option-lists', CategoryList.as_view()),
    path('book-recipe-masters/level-option-lists', LevelList.as_view()),
    path('book-recipe/my-favorite-recipes', MyFavoriteRecipe.as_view()),
    path('book-recipe/my-recipes', MyRecipe.as_view()),
    path('book-recipe/book-recipes/<int:id>', DetailRecipe.as_view()),
]