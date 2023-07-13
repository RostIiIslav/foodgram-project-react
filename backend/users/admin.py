from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from users.models import Subscription, User

admin.site.register(Subscription)


@admin.register(User)
class UserAdmin(UserAdmin):
    list_filter = ('username', 'email')
    list_display = ('username', 'email', 'first_name', 'last_name')
    search_fields = ('username', 'email')
