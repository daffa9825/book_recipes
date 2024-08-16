import logging
from .models import Recipe, Category, Level
from .serializers import RecipeSerializer
from rest_framework import status
from rest_framework.permissions import AllowAny
from django.core.paginator import Paginator
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Recipe, User, FavoriteFoods
from django.contrib.auth.models import User as AuthUser
from .serializers import RecipeSerializer, FavoriteFoodsSerializer
from rest_framework.response import Response
from django.contrib.auth import authenticate
from rest_framework.views import APIView
from django.http import JsonResponse
from rest_framework.permissions import IsAuthenticated
from django.db import IntegrityError
from datetime import datetime, timezone
from django.contrib.auth.hashers import check_password
from django.core.paginator import Paginator
import os


logger = logging.getLogger(__name__)
class SignupUser(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []
    
    def post(self, request):
        try:
            username = request.data.get('username')
            password = request.data.get('password')
            fullname = request.data.get('fullname')
            retypePassword = request.data.get('retypePassword')

            if not username or not password or not fullname or not retypePassword:
                response_data = {
                    "message" : "Username, password, fullname dan retypePassword harus diisi.",
                    "statusCode" : status.HTTP_400_BAD_REQUEST,
                    "status" : "OK"
                }
                # logger.info("Username, password harus diisi.")
                return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
            if password != retypePassword:
                response_data = {
                    "message" : "Password dan RetypePassword tidak sesuai",
                    "statusCode" : status.HTTP_400_BAD_REQUEST,
                    "status" : "ERROR"
                }
                return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

            if User.objects.filter(username=username).exists():
                response_data = {
                    "message" : "Username sudah digunakan.",
                    "statusCode" : status.HTTP_400_BAD_REQUEST,
                    "status" : "ERROR"
                }
                return Response(response_data, status=status.HTTP_400_BAD_REQUEST)


            email = f"{username}@gmail.com"
            auth_user = AuthUser(username=username, password=password, email=email, is_staff=True, is_active=True)
            auth_user.save()
            user = User(username=username, password=password, fullname=fullname)
            user.save()
            return_message = f"User {username} registered successfully!"
            response_data = {
                    "message" : return_message,
                    "statusCode" : status.HTTP_201_CREATED,
                    "status" : "OK"
                }
            # logger.info(f"User {username} berhasil dibuat")
            return Response(response_data, status=status.HTTP_201_CREATED)

        except Exception as e:
            response_data = {
                    "message" : str (e),
                    "statusCode" : status.HTTP_500_INTERNAL_SERVER_ERROR,
                    "status" : "Internal Server Error"
                }
            return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class LoginUser(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        try:
            user = User.objects.get(username=username, is_deleted=False)
            if check_password(password, user.password):
                refresh = RefreshToken.for_user(user)
                access_token = str(refresh.access_token)
                
                response_data = {
                    "data": {
                        "id" : user.id,
                        "token" : access_token,
                        "type" : "bearer",
                        "username" : user.username,
                        "role" : user.role
                    },
                    "message" : "Success Login",
                    "statusCode" : status.HTTP_200_OK,
                    "status" : "OK"
                }
                return Response(response_data, status=status.HTTP_200_OK)
            else:
                response_data = {
                    "data": {},
                    "message" : "Gagal Login, Username dan Password Salah",
                    "statusCode" : status.HTTP_400_BAD_REQUEST,
                    "status" : "ERROR"
                }
                return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
                response_data = {
                    "data": {},
                    "message" : "Gagal Login, Username dan Password Salah",
                    "statusCode" : status.HTTP_400_BAD_REQUEST,
                    "status" : "ERROR"
                }
                return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
                response_data = {
                    "data": {},
                    "message" : str (e),
                    "statusCode" : status.HTTP_500_INTERNAL_SERVER_ERROR,
                    "status" : "Internal Server Error"
                }
                return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class CategoryList(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, *args, **kwargs):
        try:
                categories = Category.objects.all()
                data = []
                for category in categories: 
                    data.append({
                        "id": category.category_id,
                        "category_name": category.category_name
                    })
                response_data = {
                    "data": data,
                    "message": "Success",
                    "statusCode": status.HTTP_200_OK,
                    "status": "OK"
                }
                return Response(response_data, status=status.HTTP_200_OK)
        except Exception as e:
            response_data = {
                "message" : str (e),
                "statusCode" : status.HTTP_500_INTERNAL_SERVER_ERROR,
                "status" : "Internal Server Error"
            }
            return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class LevelList(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, *args, **kwargs):
        try:
            levels = Level.objects.all()
            data = []
            for level in levels: 
                data.append({
                    "id": level.level_id,
                    "levelName": level.level_name
                })
            response_data = {
                "data": data,
                "message": "Success",
                "statusCode": status.HTTP_200_OK,
                "status": "OK"
            }
            return Response(response_data, status=status.HTTP_200_OK)
        except Exception as e:
            response_data = {
                "message" : str (e),
                "statusCode" : status.HTTP_500_INTERNAL_SERVER_ERROR,
                "status" : "Internal Server Error"
            }
            return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class RecipeUpdateIsFavorite(APIView):
    permission_classes = [IsAuthenticated]
    def put(self, request, id, *args, **kwargs):
        try:
            recipe = Recipe.objects.get(recipe_id=id, is_deleted=False)
            name = recipe.recipe_name
            data = request.data.copy()
            if not request.data.get('userId'):
                response_data = {
                    "message": "UserId tidak boleh kosong",
                    "statusCode": status.HTTP_400_BAD_REQUEST,
                    "status": "ERROR"
                }
                return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
            user_id = request.data.get('userId')
            user = User.objects.filter(id=user_id).first()
            if user is None:
                response_data = {
                    "message": "User tidak ditemukan",
                    "statusCode": status.HTTP_404_NOT_FOUND,
                    "status": "Not Found"
                }
                return Response(response_data, status=status.HTTP_404_NOT_FOUND)
            if recipe.is_favorite == False:
                data = {
                        'is_favorite': True,
                        'modified_by': user.username,
                        'modified_time': datetime.now(timezone.utc),
                    }
                message = f"Resep {name} berhasil ditambahkan kedalam favorit"
            else:
                data = {
                        'is_favorite': False,
                        'modified_by': user.username,
                        'modified_time': datetime.now(timezone.utc),
                    }
                message = f"Resep {name} berhasil dihapus dari favorit"
            serializer = RecipeSerializer(recipe, data=data, partial=True) 
            if serializer.is_valid():
                serializer.save()
                favorite_exists = FavoriteFoods.objects.filter(recipe=id).exists()
            
                if not favorite_exists:
                    data_fav = {
                        "recipe": id,
                        "user": user_id,
                        "created_by": user.username
                    }
                    fav_serializer = FavoriteFoodsSerializer(data=data_fav, partial=True) 
                    if fav_serializer.is_valid():
                        fav_serializer.save()
                else:
                    pass
                
                response_data = {
                    "total" : 1,
                    "data" : "",
                    "message": message,
                    "statusCode": status.HTTP_200_OK,
                    "status": "OK"
                }
                return Response(response_data, status=status.HTTP_200_OK)

            response_data = {
                "message": serializer.errors,
                "statusCode": status.HTTP_400_BAD_REQUEST,
                "status": "ERROR"
            }
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

        except Recipe.DoesNotExist:
            response_data = {
                "message": "Resep tidak ditemukan",
                "statusCode": status.HTTP_404_NOT_FOUND,
                "status": "Not Found"
            }
            return Response(response_data, status=status.HTTP_404_NOT_FOUND)
        
        except Exception as e:
            response_data = {
                "message": str(e),
                "statusCode": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "status": "Internal Server Error"
            }
            return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class MyFavoriteRecipe(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, *args, **kwargs):
        try:
            user_id = request.query_params.get('userId')
            recipe_name = request.query_params.get('recipeName', '')
            level_id = request.query_params.get('levelId')
            category_id = request.query_params.get('categoryId')
            time = request.query_params.get('time')
            sort_by = request.query_params.get('sortBy', 'recipe_name,asc')
            page_size = int(request.query_params.get('pageSize', 10)) 
            page_number = int(request.query_params.get('pageNumber', 1)) 

            recipes = Recipe.objects.filter(is_deleted=False, is_favorite=True).select_related('category', 'level')

            # Filter berdasarkan parameter
            if user_id:
                recipes = recipes.filter(user_id=user_id)
            if recipe_name:
                recipes = recipes.filter(recipe_name__icontains=recipe_name)
            if level_id:
                recipes = recipes.filter(level_id=level_id)
            if category_id:
                recipes = recipes.filter(category_id=category_id)
            if time:
                recipes = recipes.filter(time=time)

            # Sorting
            sort_mapping = {
                'recipeName': 'recipe_name',
                'timeCook': 'time_cook',
            }
            if sort_by:
                field, direction = sort_by.split(',')
                db_field = sort_mapping.get(field, field)  
                if direction == 'asc':
                    recipes = recipes.order_by(db_field)
                else:
                    recipes = recipes.order_by(f'-{db_field}')

            # Pagination
            paginator = Paginator(recipes, page_size)
            page = paginator.get_page(page_number)

    
            data = []
            for recipe in page.object_list:
                data.append({
                    "recipeId": recipe.recipe_id,
                    "categories": {
                        "categoryId": recipe.category.category_id,
                        "categoryName": recipe.category.category_name,
                    },
                    "levels": {
                        "levelId": recipe.level.level_id,
                        "levelName": recipe.level.level_name,
                    },
                    "recipeName": recipe.recipe_name,
                    "imageUrl": recipe.image_url,
                    "time": recipe.time,
                    "isFavorite": recipe.is_favorite
                })

            response_data = {
                "total": paginator.count,
                "data": data,
                "message": "Berhasil memuat resep makanan",
                "statusCode": status.HTTP_200_OK,
                "status": "OK"
            }
            return Response(response_data, status=status.HTTP_200_OK)
        
        except Exception as e:
            response_data = {
                "message" : str (e),
                "statusCode" : status.HTTP_500_INTERNAL_SERVER_ERROR,
                "status" : "Internal Server Error"
            }
            return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class MyRecipe(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, *args, **kwargs):
        try:
            user_id = request.query_params.get('userId')
            recipe_name = request.query_params.get('recipeName', '')
            level_id = request.query_params.get('levelId')
            category_id = request.query_params.get('categoryId')
            time = request.query_params.get('time')
            sort_by = request.query_params.get('sortBy', 'recipe_name,asc')
            page_size = int(request.query_params.get('pageSize', 10)) 
            page_number = int(request.query_params.get('pageNumber', 1)) 

            recipes = Recipe.objects.filter(is_deleted=False, user_id=request.user.id).select_related('category', 'level')

            # Filter berdasarkan parameter
            if user_id:
                recipes = recipes.filter(user_id=user_id)
            if recipe_name:
                recipes = recipes.filter(recipe_name__icontains=recipe_name)
            if level_id:
                recipes = recipes.filter(level_id=level_id)
            if category_id:
                recipes = recipes.filter(category_id=category_id)
            if time:
                recipes = recipes.filter(time=time)

            # Sorting
            sort_mapping = {
                'recipeName': 'recipe_name',
                'timeCook': 'time_cook',
            }
            if sort_by:
                field, direction = sort_by.split(',')
                db_field = sort_mapping.get(field, field)  
                if direction == 'asc':
                    recipes = recipes.order_by(db_field)
                else:
                    recipes = recipes.order_by(f'-{db_field}')

            # Pagination
            paginator = Paginator(recipes, page_size)
            page = paginator.get_page(page_number)

    
            data = []
            for recipe in page.object_list:
                data.append({
                    "recipeId": recipe.recipe_id,
                    "categories": {
                        "categoryId": recipe.category.category_id,
                        "categoryName": recipe.category.category_name,
                    },
                    "levels": {
                        "levelId": recipe.level.level_id,
                        "levelName": recipe.level.level_name,
                    },
                    "recipeName": recipe.recipe_name,
                    "imageUrl": recipe.image_url,
                    "time": recipe.time,
                    "isFavorite": recipe.is_favorite
                })

            response_data = {
                "total": paginator.count,
                "data": data,
                "message": "Berhasil memuat resep makanan",
                "statusCode": status.HTTP_200_OK,
                "status": "OK"
            }
            return Response(response_data, status=status.HTTP_200_OK)
        
        except Exception as e:
            response_data = {
                "message" : str (e),
                "statusCode" : status.HTTP_500_INTERNAL_SERVER_ERROR,
                "status" : "Internal Server Error"
            }
            return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class DetailRecipe(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, id, *args, **kwargs):
        try:
            recipe = Recipe.objects.select_related('category', 'level').get(recipe_id=id)

            response_data = {
                "data": {
                    "recipeId": recipe.recipe_id,
                    "categories": {
                        "categoryId": recipe.category.category_id,
                        "categoryName": recipe.category.category_name,
                    },
                    "levels": {
                        "levelId": recipe.level.level_id,
                        "levelName": recipe.level.level_name,
                    },
                    "recipeName": recipe.recipe_name,
                    "imageUrl": recipe.image_url,
                    "time": recipe.time,
                    "isFavorite": recipe.is_favorite
                },
                "message": "Berhasil memuat resep makanan",
                "statusCode": status.HTTP_200_OK,
                "status": "OK"
            }
            return Response(response_data, status=status.HTTP_200_OK)

        except Recipe.DoesNotExist:
            response_data = {
                "message": "Resep tidak ditemukan",
                "statusCode": status.HTTP_404_NOT_FOUND,
                "status": "Not Found"
            }
            return Response(response_data, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            response_data = {
                "message" : str (e),
                "statusCode" : status.HTTP_500_INTERNAL_SERVER_ERROR,
                "status" : "Internal Server Error"
            }
            return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class RecipeView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, *args, **kwargs):
        try:
            request.data['created_by'] = request.user.username
            request.data['user'] = request.user.id
            recipe_name = request.data.get('recipe_name')
            category_id = request.data.get('category')
            level_id = request.data.get('level')
            request.data['is_deleted'] = False
            request.data['is_favorite'] = False
            request.data['created_time'] = datetime.now(timezone.utc)
            image_file = request.FILES.get('image')
            if image_file:
                valid_extensions = ['.jpg', '.jpeg', '.png']
                file_ext = os.path.splitext(image_file.name)[1].lower()

                if file_ext not in valid_extensions:
                    return Response({
                        "message": "Hanya file dengan ekstensi jpg, jpeg, dan png yang diperbolehkan",
                        "statusCode": status.HTTP_400_BAD_REQUEST,
                        "status": "ERROR"
                    }, status=status.HTTP_400_BAD_REQUEST)

                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                new_filename = f"{recipe_name}_{category_id}_{level_id}_{timestamp}{file_ext}"

                file_path = os.path.join('media/images', new_filename)
                with open(file_path, 'wb+') as destination:
                    for chunk in image_file.chunks():
                        destination.write(chunk)
            else:
                new_filename = None
            
            request.data['image_filename'] = new_filename
            request.data['image_url'] = f"{request.scheme}://{request.get_host()}/media/{new_filename}"
            
            serializer = RecipeSerializer(data=request.data)
            if serializer.is_valid():
                instance = serializer.save()
                response_data = {
                    "message" : "Resep berhasil ditambahkan",
                    "statusCode" : status.HTTP_201_CREATED,
                    "status" : "Created"
                }
                return Response(response_data, status=status.HTTP_201_CREATED)
            response_data = {
                "message" : serializer.errors,
                "statusCode" : status.HTTP_400_BAD_REQUEST,
                "status" : "ERROR"
            }
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            response_data = {
                "message" : str (e),
                "statusCode" : status.HTTP_500_INTERNAL_SERVER_ERROR,
                "status" : "Internal Server Error"
            }
            return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    def get(self, request, *args, **kwargs):
        try:
            user_id = request.query_params.get('userId')
            recipe_name = request.query_params.get('recipeName', '')
            level_id = request.query_params.get('levelId')
            category_id = request.query_params.get('categoryId')
            time = request.query_params.get('time')
            sort_by = request.query_params.get('sortBy', 'recipe_name,asc')
            page_size = int(request.query_params.get('pageSize', 10)) 
            page_number = int(request.query_params.get('pageNumber', 1)) 

            recipes = Recipe.objects.filter(is_deleted=False).select_related('category', 'level')

            # Filter berdasarkan parameter
            if user_id:
                recipes = recipes.filter(user_id=user_id)
            if recipe_name:
                recipes = recipes.filter(recipe_name__icontains=recipe_name)
            if level_id:
                recipes = recipes.filter(level_id=level_id)
            if category_id:
                recipes = recipes.filter(category_id=category_id)
            if time:
                recipes = recipes.filter(time=time)

            # Sorting
            sort_mapping = {
                'recipeName': 'recipe_name',
                'timeCook': 'time_cook',
            }
            if sort_by:
                field, direction = sort_by.split(',')
                db_field = sort_mapping.get(field, field)  
                if direction == 'asc':
                    recipes = recipes.order_by(db_field)
                else:
                    recipes = recipes.order_by(f'-{db_field}')

            # Pagination
            paginator = Paginator(recipes, page_size)
            page = paginator.get_page(page_number)

    
            data = []
            for recipe in page.object_list:
                data.append({
                    "recipeId": recipe.recipe_id,
                    "categories": {
                        "categoryId": recipe.category.category_id,
                        "categoryName": recipe.category.category_name,
                    },
                    "levels": {
                        "levelId": recipe.level.level_id,
                        "levelName": recipe.level.level_name,
                    },
                    "recipeName": recipe.recipe_name,
                    "imageUrl": recipe.image_url,
                    "time": recipe.time,
                    "isFavorite": recipe.is_favorite
                })

            response_data = {
                "total": paginator.count,
                "data": data,
                "message": "Berhasil memuat resep makanan",
                "statusCode": status.HTTP_200_OK,
                "status": "OK"
            }
            return Response(response_data, status=status.HTTP_200_OK)
        
        except Exception as e:
            response_data = {
                "message" : str (e),
                "statusCode" : status.HTTP_500_INTERNAL_SERVER_ERROR,
                "status" : "Internal Server Error"
            }
            return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    