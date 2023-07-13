from django.contrib import admin
from django.urls import include, path
from djoser.views import TokenCreateView, TokenDestroyView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('rest_framework.urls', namespace='rest_framework')),
    path('api/', include('api.urls')),
    path('api/auth/', include('djoser.urls')),
    path('api/auth/token/login/', TokenCreateView.as_view(),
         name='token_login'),
    path('api/auth/token/logout/', TokenDestroyView.as_view(),
         name='token_logout'),
]
