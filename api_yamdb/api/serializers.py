from rest_framework import serializers
from rest_framework.validators import ValidationError

from reviews.models import Category, Comment, Genre, Review, Title, User


class UsersSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "username",
            "email",
            "first_name",
            "last_name",
            "bio",
            "role",
        )


class NotAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        exclude = ("id",)
        read_only_fields = ("role",)


class GetTokenSerializer(serializers.ModelSerializer):
    username = serializers.CharField(required=True)
    confirmation_code = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = ("username", "confirmation_code")


class SignUpSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("email", "username")


class GenresSerializer(serializers.ModelSerializer):
    """Серилизатор для Genres."""

    class Meta:
        model = Genre
        exclude = ("id",)
        lookup_field = "slug"


class CategoriesSerializer(serializers.ModelSerializer):
    """Серилизатор для Categories"""

    class Meta:
        model = Category
        exclude = ("id",)
        lookup_field = "slug"


class TitleCreateSerializer(serializers.ModelSerializer):
    """Серилизатор для создания тайтла."""

    genre = serializers.SlugRelatedField(
        slug_field="slug",
        queryset=Genre.objects.all(),
        many=True,
    )
    category = serializers.SlugRelatedField(
        slug_field="slug",
        queryset=Category.objects.all(),
    )

    class Meta:
        model = Title
        fields = "__all__"


class ReviewSerializer(serializers.ModelSerializer):
    """Серилизатор для Review."""

    author = serializers.SlugRelatedField(
        read_only=True,
        slug_field="username",
    )

    class Meta:
        model = Review
        fields = ("id", "text", "author", "score", "pub_date")

    def validate(self, data):
        """Проверка на повторное ревью"""
        request = self.context["request"]
        title = self.context["title"]
        if (
            request.method == "POST"
            and Review.objects.filter(title=title, author=request.user).exists()
        ):
            raise ValidationError("К произведению можно оставить только одно ревью")
        return data


class CommentsSerializer(serializers.ModelSerializer):
    """Серилизатор для Comment."""

    author = serializers.SlugRelatedField(read_only=True, slug_field="username")
    review = serializers.SlugRelatedField(read_only=True, slug_field="text")

    class Meta:
        model = Comment
        fields = "__all__"
