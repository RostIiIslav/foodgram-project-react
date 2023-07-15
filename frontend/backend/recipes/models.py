from django.db import models

from users.models import User


class Ingredient(models.Model):
    measurement_unit = models.CharField(max_length=10,
                                        verbose_name='Единица измерения')
    name = models.CharField(max_length=120,
                            verbose_name='Название ', )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(unique=True, max_length=40,
                            verbose_name='Название')
    slug = models.SlugField(unique=True, verbose_name='tag')
    color = models.CharField(unique=True, max_length=40,
                             verbose_name='hex')

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    text = models.TextField(verbose_name='Описание')
    name = models.CharField(max_length=90,
                            verbose_name='Название')
    image = models.ImageField(verbose_name='Изображение',
                              upload_to='recipes/', )
    tags = models.ManyToManyField(Tag, verbose_name='Теги',
                                  related_name='tag_recipes')
    pub_date = models.DateTimeField(verbose_name='Дата добавления',
                                    auto_now_add=True, db_index=True)
    author = models.ForeignKey(User, verbose_name='Автор',
                               on_delete=models.CASCADE,
                               related_name='recipes')
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления рецепта')
    ingredients = models.ManyToManyField(Ingredient,
                                         through='IngredientRecipe',
                                         verbose_name='Ингредиенты')

    class Meta:
        ordering = ['-pub_date']
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class IngredientRecipe(models.Model):
    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество ингредиентов в рецепте')
    recipe = models.ForeignKey(Recipe, verbose_name='Рецепт',
                               on_delete=models.CASCADE,
                               related_name='recipe_ingredients')
    ingredient = models.ForeignKey(
        Ingredient, verbose_name='Ингредиент', on_delete=models.CASCADE,
        related_name='recipe_ingredients')


class Cart(models.Model):
    user = models.ForeignKey(User, verbose_name='Кому принадлежат покупки',
                             on_delete=models.CASCADE, related_name='carts')
    recipe = models.ForeignKey(Recipe, verbose_name='Рецепт',
                               on_delete=models.CASCADE, related_name='carts')

    class Meta:
        ordering = ['-id']
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'


class Favorite(models.Model):
    user = models.ForeignKey(User, verbose_name='Пользователь',
                             on_delete=models.CASCADE,
                             related_name='favorites')
    recipe = models.ForeignKey(Recipe, verbose_name='Рецепт',
                               on_delete=models.CASCADE,
                               related_name='favorites')

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранные'
