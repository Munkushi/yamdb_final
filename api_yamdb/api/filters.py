import django_filters
from reviews.models import Title


class TitleFilters(django_filters.FilterSet):
    """Класс для фильтра модели Title."""

    category = django_filters.rest_framework.CharFilter(
        field_name="category__slug"
    )
    # фильтр по слагу поля
    genre = django_filters.rest_framework.CharFilter(field_name="genre__slug")
    name = django_filters.rest_framework.CharFilter(
        field_name="name", lookup_expr="icontains"
    )
    # icontains: Фильтрация размытия
    year = django_filters.rest_framework.NumberFilter(field_name="year")

    class Meta:
        model = Title
        fields = ("category", "genre", "name", "year")
