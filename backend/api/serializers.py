import base64

from django.contrib.auth.password_validation import validate_password
from django.core.files.base import ContentFile
from djoser.serializers import UserCreateSerializer
from djoser.serializers import UserSerializer
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from recipes.models import Ingredient, IngredientRecipe, Recipe, Tag
from users.models import User

MIN_INGREDIENT_AMOUNT = 0
MAX_INGREDIENT_AMOUNT = 1000


class CustomUserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email', 'id',
            'username', 'first_name', 'last_name',
            'is_subscribed')

    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        return not user.is_anonymous and \
            obj.author_subscriptions.filter(user=user).exists()


class CustomUserCreateSerializer(UserCreateSerializer):
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password')
        validators = (
            UniqueTogetherValidator(
                queryset=User.objects.all(),
                fields=('username', 'email')
            ),
        )


class SubscriptionSerializer(CustomUserSerializer):
    recipes_count = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name',
                  'last_name', 'is_subscribed', 'recipes_count', 'recipes')

    def get_recipes_count(self, obj):
        return obj.recipes.count()

    def get_recipes(self, obj):
        recipe_limit = int(self.context['request'].GET.get('recipes_limit'))
        recipes = obj.recipes.all()
        recipes = recipes[:recipe_limit] if recipe_limit else recipes
        serializer = DetailRecipeSerializer(recipes, many=True)
        return serializer.data


class ChangePasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(write_only=True)
    current_password = serializers.CharField(write_only=True)

    def validate_new_password(self, value):
        validate_password(value)
        return value

    def validate_current_password(self, value):
        user = self.context['request'].user
        if user.check_password(value):
            return value

        raise serializers.ValidationError(
                'Старый пароль не совпадает'
            )


class IngredientsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class TagsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class RecipeIngredientsSerializer(serializers.ModelSerializer):
    id = serializers.CharField(read_only=True, source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit', read_only=True)

    class Meta:
        model = IngredientRecipe
        fields = (
            'id',
            'name',
            'measurement_unit',
            'amount'
        )


class CreateRecipeIngredientsSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all(),
                                            source='ingredient',
                                            write_only=True)

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'amount')


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class DetailRecipeSerializer(serializers.ModelSerializer):
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'cooking_time', 'image')


class RecipeSerializer(serializers.ModelSerializer):
    image = Base64ImageField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    tags = TagsSerializer(many=True, read_only=True)
    ingredients = RecipeIngredientsSerializer(source='recipe_ingredients',
                                              many=True, read_only=True)
    author = CustomUserSerializer(read_only=True)

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'text', 'author', 'image', 'tags',
                  'ingredients', 'cooking_time', 'is_in_shopping_cart',
                  'is_favorited')

    def get_is_favorited(self, obj):
        user = self.context['request'].user
        return not user.is_anonymous and \
            obj.favorites.filter(user=user).exists()

    def get_is_in_shopping_cart(self, obj):
        user = self.context['request'].user
        return not user.is_anonymous and obj.carts.filter(user=user).exists()


class RecipeCreateSerializer(RecipeSerializer):
    tags = serializers.PrimaryKeyRelatedField(queryset=Tag.objects.only('id'),
                                              many=True, write_only=True)
    ingredients = CreateRecipeIngredientsSerializer(many=True,
                                                    write_only=True)

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'text', 'image', 'tags', 'ingredients',
                  'cooking_time', 'is_favorited', 'is_in_shopping_cart')

    def validate_tags(self, tags):
        if not tags:
            raise serializers.ValidationError('Нужны тэги')
        unique_tags = []
        for tag in tags:
            if tag.id in unique_tags:
                continue
            unique_tags.append(tag)

        return unique_tags

    def create(self, validated_data):
        tags = validated_data.pop('tags', [])
        ingredients = validated_data.pop('ingredients', [])
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        for ingredient in ingredients:
            IngredientRecipe.objects.create(recipe=recipe,
                                            ingredient=ingredient[
                                                'ingredient'],
                                            amount=ingredient['amount'])
        return recipe

    def update(self, instance, validated_data):
        tags = validated_data.pop('tags', [])
        ingredients = validated_data.pop('ingredients', [])
        super().update(instance, validated_data)
        instance.tags.set(tags)
        IngredientRecipe.objects.filter(recipe=instance).delete()
        for ingredient in ingredients:
            IngredientRecipe.objects.create(recipe=instance,
                                            ingredient=ingredient[
                                                'ingredient'],
                                            amount=ingredient['amount'])
        return instance

    def validate_ingredients(self, ingredients):
        for ingredient in ingredients:
            if not (MIN_INGREDIENT_AMOUNT <
                    ingredient['amount'] < MAX_INGREDIENT_AMOUNT):
                raise serializers.ValidationError(
                    'Неверное кол-во ингредиентов')
        return ingredients
