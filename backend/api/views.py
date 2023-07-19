from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import (
    IsAuthenticated, BasePermission,
    IsAuthenticatedOrReadOnly)

from rest_framework.response import Response

from api.filters import RecipeFilter, IngredientsFilter
from api.serializers import (ChangePasswordSerializer,
                             SubscriptionSerializer,
                             CustomUserCreateSerializer,
                             CustomUserSerializer, IngredientsSerializer,
                             RecipeCreateSerializer,
                             RecipeSerializer, DetailRecipeSerializer,
                             TagsSerializer)
from recipes.models import (Favorite, Ingredient,
                            Recipe, Tag, Cart, IngredientRecipe)
from users.models import Subscription, User


class IngredientsViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    search_fields = ('^name',)
    serializer_class = IngredientsSerializer
    filter_backends = [IngredientsFilter]
    pagination_class = None


class TagsViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagsSerializer
    pagination_class = None


class ResultsSetPagination(PageNumberPagination):
    max_page_size = 100
    page_size_query_param = 'limit'


class RecipesPagination(PageNumberPagination):
    page_size_query_param = 'limit'
    max_page_size = 10

class IsAuthorRecipe(BasePermission):
    def has_permission(self, request, view):
        return view.get_object().author == request.user


class RecipesViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeCreateSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    pagination_class = RecipesPagination
    permission_classes = (IsAuthorRecipe,)

    def get_permissions(self):
        if self.action in ['update', 'destroy', 'partial_update', 'partial']:
            permission_classes = (IsAuthenticated, IsAuthorRecipe)
        else:
            permission_classes = (IsAuthenticatedOrReadOnly,)
        return [permission() for permission in permission_classes]

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return RecipeSerializer
        return super().get_serializer_class()

    def dispatch(self, request, *args, **kwargs):
        if 'is_in_shopping_cart' in request.GET:
            self.pagination_class = ResultsSetPagination
        return super().dispatch(request, *args, **kwargs)

    def get_object(self):
        return get_object_or_404(Recipe, id=self.kwargs['pk'])

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(
        detail=True,
        methods=['POST', 'DELETE'],
        permission_classes=[IsAuthenticated]
    )
    def favorite(self, request, *args, **kwargs):
        recipe = get_object_or_404(Recipe, id=self.kwargs['pk'])
        if request.method == 'POST':
            Favorite.objects.create(recipe=recipe, user=request.user)
            serializer = DetailRecipeSerializer(recipe, context={
                'request': request})
            return Response(serializer.data)

        Favorite.objects.filter(recipe=recipe, user=request.user).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['POST', 'DELETE'],
            permission_classes=[IsAuthenticated])
    def shopping_cart(self, request, *args, **kwargs):
        recipe = get_object_or_404(Recipe, id=self.kwargs['pk'])
        if self.request.method == 'POST':
            Cart.objects.create(recipe=recipe, user=request.user)
            serializer = DetailRecipeSerializer(recipe, context={
                'request': self.request})
            return Response(serializer.data, status=status.HTTP_200_OK)

        Cart.objects.filter(recipe=recipe, user=self.request.user).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, permission_classes=[IsAuthenticated])
    def download_shopping_cart(self, *args, **kwargs):
        items = IngredientRecipe.objects.filter(
            recipe__carts__user=self.request.user).values(
            'ingredient__name',
            'ingredient__measurement_unit').annotate(
            total_am=Sum('amount')).order_by()
        list_shopping = 'Список покупок\n'
        for item in items:
            list_shopping += (f'{item["ingredient__name"]} '
                              f'({item["ingredient__measurement_unit"]}) - '
                              f'{item["total_am"]}\n')
        response = HttpResponse(content=list_shopping,
                                content_type='text/plain')
        response['Content-Disposition'] = ('attachment; '
                                           'filename="shopping_list.txt"')
        return response


class UsersViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer

    def get_serializer_class(self):
        if self.action in ['create', 'update']:
            return CustomUserCreateSerializer
        return super().get_serializer_class()

    @action(detail=False, methods=['GET'],
            permission_classes=[IsAuthenticated])
    def subscriptions(self, request, *args, **kwargs):
        subscriptions = User.objects.filter(
            author_subscriptions__user=request.user)
        page = self.paginate_queryset(subscriptions)
        serializer = SubscriptionSerializer(page, many=True,
                                            context={'request': request})
        return self.get_paginated_response(serializer.data)

    @action(detail=False, methods=['GET'],
            permission_classes=[IsAuthenticated])
    def me(self, request, *args, **kwargs):
        user = get_object_or_404(User, id=request.user.id)
        serializer = self.get_serializer(user)
        return Response(serializer.data)

    @action(
        detail=True,
        methods=['POST', 'DELETE'],
        permission_classes=[IsAuthenticated]
    )
    def subscribe(self, request, *args, **kwargs):
        author = get_object_or_404(User, id=kwargs['pk'])
        if self.request.method == 'DELETE':
            author.author_subscriptions.filter(user=request.user).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        Subscription.objects.create(author=author, user=request.user)
        serializer = self.get_serializer(author)
        return Response(serializer.data)

    @action(
        detail=False,
        methods=['POST'],
        permission_classes=[IsAuthenticated]
    )
    def set_password(self, request, *args, **kwargs):
        serializer = ChangePasswordSerializer(data=request.data,
                                              context={'request': request})
        serializer.is_valid(raise_exception=True)
        self.request.user.set_password(
            serializer.validated_data['new_password'])
        self.request.user.save()
        return Response(data={'status': f'set password '
                                        f' {request.user.username}'})
