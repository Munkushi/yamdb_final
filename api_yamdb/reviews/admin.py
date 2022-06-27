from django.contrib import admin

from .models import Category, Genre, Title, User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """Админка для модели User."""

    list_display = (
        "username",
        "email",
        "role",
        "bio",
        "first_name",
        "last_name",
        "confirmation_code",
    )
    search_fields = (
        "username",
        "role",
    )
    list_filter = ("username",)
    empty_value_display = "-пусто-"


class CategoriesAdmin(admin.ModelAdmin):
    """Админка для модели Category."""

    search_fields = ("name",)
    empty_value_display = "-пусто-"
    list_display = ("name", "slug")


class GenresAdmin(admin.ModelAdmin):
    """Админка для модели Genres."""

    empty_value_display = "-пусто-"
    search_fields = ("name",)
    list_display = ("name", "slug")


class TitleAdmin(admin.ModelAdmin):
    """Админка для модели Title."""

    empty_value_display = "-пусто-"
    list_display = ("category", "year", "name", "desription")
    filter_fields = ("year", "category", "genre")


admin.register(Category, CategoriesAdmin)
admin.register(Genre, GenresAdmin)
admin.register(Title, TitleAdmin)
