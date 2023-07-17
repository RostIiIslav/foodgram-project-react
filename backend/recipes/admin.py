from django.contrib import admin

from recipes.models import (
    Cart, Favorite, Ingredient, IngredientRecipe, Recipe, Tag)

admin.site.register(Favorite)
admin.site.register(IngredientRecipe)
admin.site.register(Tag)
admin.site.register(Cart)


class IngredientInline(admin.TabularInline):
    model = Recipe.ingredients.through
    min_num = 1


class IngredientAdmin(admin.ModelAdmin):
    list_filter = ('name',)
    list_display = ('name', 'measurement_unit')


class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'author', 'favorites')
    list_filter = ('author', 'name', 'tags')
    inlines = (
        IngredientInline,
    )

    def favorites(self, obj):
        return obj.favorites.count()

    favorites.short_description = 'Находится в избранном'


admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Ingredient, IngredientAdmin)
