from django.contrib import admin
from .models import User
from django.contrib.auth.admin import UserAdmin


class CustomUserAdmin(UserAdmin):
    list_display = ("id", "username", "email", "phone_number")
    search_field = ("username", "email")


admin.site.register(User, CustomUserAdmin)
