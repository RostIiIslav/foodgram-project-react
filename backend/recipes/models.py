from colorfield.fields import ColorField
from django.db import models
from rest_framework.exceptions import ValidationError

from users.models import User


class Ingredient(models.Model):
    measurement_unit = models.CharField('Единица измерения', max_length=10)
    name = models.CharField('Название', max_length=120)

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return self.name[:50]


class Tag(models.Model):
    name = models.CharField('Название', unique=True, max_length=40)
    slug = models.SlugField('tag', unique=True)
    color = ColorField('hex', default='#FF0000', unique=True)

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name[:50]


class Recipe(models.Model):
    text = models.TextField('Описание', unique=True)
    name = models.CharField('Название', max_length=90)
    image = models.ImageField('Изображение', upload_to='recipes/')
    tags = models.ManyToManyField(Tag, verbose_name='Теги',
                                  related_name='tag_recipes')
    pub_date = models.DateTimeField('Дата добавления',
                                    auto_now_add=True, db_index=True)
    author = models.ForeignKey(User, verbose_name='Автор',
                               on_delete=models.CASCADE,
                               related_name='recipes')
    cooking_time = models.PositiveSmallIntegerField(
        'Время приготовления рецепта')
    ingredients = models.ManyToManyField(Ingredient,
                                         through='IngredientRecipe',
                                         verbose_name='Ингредиенты')

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name[:50]


class IngredientRecipe(models.Model):
    amount = models.PositiveSmallIntegerField(
        'Количество ингредиентов в рецепте')
    recipe = models.ForeignKey(Recipe, verbose_name='Рецепт',
                               on_delete=models.CASCADE,
                               related_name='recipe_ingredients')
    ingredient = models.ForeignKey(
        Ingredient, verbose_name='Ингредиент', on_delete=models.CASCADE,
        related_name='recipe_ingredients')

    class Meta:
        ordering = ['-id']
        verbose_name = 'Рецепт и Ингридиент'
        verbose_name_plural = 'Рецепты и Ингридиенты'
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='recipe_ingredient_unique'
            )
        ]


class Cart(models.Model):
    user = models.ForeignKey(User, verbose_name='Кому принадлежат покупки',
                             on_delete=models.CASCADE, related_name='carts')
    recipe = models.ForeignKey(Recipe, verbose_name='Рецепт',
                               on_delete=models.CASCADE, related_name='carts')

    def clean(self):
        if Cart.objects.filter(user=self.user, recipe=self.recipe).exists():
            raise ValidationError('Рецепт уже есть в корзине')

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    class Meta:
        ordering = ('-id',)
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'

    def __str__(self):
        return f'Рецепт {self.recipe} Пользователь {self.user}'


class Favorite(models.Model):
    user = models.ForeignKey(User, verbose_name='Пользователь',
                             on_delete=models.CASCADE,
                             related_name='favorites')
    recipe = models.ForeignKey(Recipe, verbose_name='Рецепт',
                               on_delete=models.CASCADE,
                               related_name='favorites')

    def clean(self):
        if Favorite.objects.filter(user=self.user,
                                   recipe=self.recipe).exists():
            raise ValidationError('Рецепт уже есть в избранном')

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранные'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='favorite_recipe_user_unique'
            )
        ]

    def __str__(self):
        return f'Рецепт {self.recipe} Пользователь {self.user}'
