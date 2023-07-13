from rest_framework import routers

from api.views import (IngredientsViewSet, RecipesViewSet, TagsViewSet,
                       UsersViewSet)

router = routers.DefaultRouter()
router.register('recipes', RecipesViewSet, basename='recipes')
router.register('users', UsersViewSet, basename='users')
router.register('tags', TagsViewSet, basename='tags')
router.register('ingredients', IngredientsViewSet, basename='ingredients')

urlpatterns = router.urls
