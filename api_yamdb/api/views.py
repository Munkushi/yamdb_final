from django.conf import settings
from django.core.mail import EmailMessage
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import (
    SAFE_METHODS,
    IsAuthenticated,
    IsAuthenticatedOrReadOnly,
)
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from reviews.models import Category, Genre, Review, Title, User

from .filters import TitleFilters
from .mixins import MixinForMainModels
from .permissions import (
    AdminOnly,
    AdminOrReadOnly,
    IsAuthorOrHasRightsOrReadOnly,
)
from .serializers import (
    CategoriesSerializer,
    CommentsSerializer,
    GenresSerializer,
    GetTokenSerializer,
    NotAdminSerializer,
    ReviewSerializer,
    SignUpSerializer,
    TitleCreateSerializer,
    TitlesReadSerializer,
    UsersSerializer,
)


class UsersViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UsersSerializer
    permission_classes = (
        IsAuthenticated,
        AdminOnly,
    )
    lookup_field = "username"
    filter_backends = (SearchFilter,)
    search_fields = ("username",)

    @action(
        methods=("GET", "PATCH"),
        detail=False,
        permission_classes=(IsAuthenticated,),
    )
    def me(self, request):
        serializer = UsersSerializer(request.user)
        if request.method == "PATCH":
            if request.user.is_admin:
                serializer = UsersSerializer(
                    request.user, data=request.data, partial=True
                )
            else:
                serializer = NotAdminSerializer(
                    request.user, data=request.data, partial=True
                )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.data)


class APIGetToken(APIView):
    """
    Получение JWT-токена в обмен на username и confirmation code.
    Права доступа: Доступно без токена. Пример тела запроса:
    {
        "username": "string",
        "confirmation_code": "string"
    }
    """

    def post(self, request):
        serializer = GetTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        try:
            user = User.objects.get(username=data["username"])
        except User.DoesNotExist:
            return Response(
                {"username": "Пользователь не найден!"},
                status=status.HTTP_404_NOT_FOUND,
            )
        if data.get("confirmation_code") == user.confirmation_code:
            token = RefreshToken.for_user(user).access_token
            return Response(
                {"token": str(token)}, status=status.HTTP_201_CREATED
            )
        return Response(
            {"confirmation_code": "Неверный код подтверждения!"},
            status=status.HTTP_400_BAD_REQUEST,
        )


class APISignup(APIView):
    """
    Получить код подтверждения на переданный email.
    Права доступа:
    Доступно без токена.
    Использовать имя "me" в качестве username запрещено.
    Поля email и
    username должны быть уникальными. Пример тела запроса:
    {
        "email": "string",
        "username": "string"
    }
    """

    permission_classes = (permissions.AllowAny,)

    @staticmethod
    def send_email(data):
        email = EmailMessage(
            subject=data["email_subject"],
            body=data["email_body"],
            to=[data["to_email"]],
            from_email=[data["from_email"]],
        )
        email.send()

    def post(self, request):
        serializer = SignUpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        email_body = (
            f"Доброе время суток, {user.username}."
            f"\nКод подтвержения для доступа к API: {user.confirmation_code}"
        )
        data = {
            "email_body": email_body,
            "to_email": user.email,
            "from_email": settings.DEFAULT_FROM_EMAIL,
            "email_subject": "Код подтвержения для доступа к API!",
        }
        self.send_email(data)
        return Response(serializer.data, status=status.HTTP_200_OK)


class GenresViewSet(MixinForMainModels):
    """Viewset для Genres-модели."""

    queryset = Genre.objects.all()
    serializer_class = GenresSerializer
    permission_classes = (AdminOrReadOnly,)
    search_fields = ("name",)
    filter_backends = (SearchFilter,)
    lookup_field = "slug"


class TitlesViewSet(viewsets.ModelViewSet):
    """Viewset для Titles-модели."""

    queryset = Title.objects.annotate(rating=Avg("reviews__score"))
    permission_classes = (AdminOrReadOnly,)
    filterset_class = TitleFilters
    filter_backends = (DjangoFilterBackend,)
    pagination_class = LimitOffsetPagination

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return TitlesReadSerializer
        return TitleCreateSerializer


class CategoriesViewSet(MixinForMainModels):
    """Viewset для Category-модели."""

    queryset = Category.objects.all()
    serializer_class = CategoriesSerializer
    permission_classes = (AdminOrReadOnly,)
    search_fields = ("name",)
    filter_backends = (SearchFilter,)
    lookup_field = "slug"


class ReviewViewSet(viewsets.ModelViewSet):
    """Viewset для Review-модели."""

    serializer_class = ReviewSerializer
    permission_classes = (
        IsAuthorOrHasRightsOrReadOnly,
        IsAuthenticatedOrReadOnly,
    )

    def get_serializer_context(self):
        context = super(ReviewViewSet, self).get_serializer_context()
        title = get_object_or_404(Title, id=self.kwargs.get("title_id"))
        context.update({"title": title})
        return context

    def get_queryset(self):
        title = get_object_or_404(Title, id=self.kwargs.get("title_id"))
        new_queryset = title.reviews.all()
        return new_queryset

    def perform_create(self, serializer):
        title = get_object_or_404(Title, id=self.kwargs.get("title_id"))
        serializer.save(author=self.request.user, title=title)


class CommentsViewSet(viewsets.ModelViewSet):
    """Viewset для Comment-модели."""

    serializer_class = CommentsSerializer
    permission_classes = (
        IsAuthorOrHasRightsOrReadOnly,
        IsAuthenticatedOrReadOnly,
    )

    def get_queryset(self):
        review = get_object_or_404(
            Review,
            title=self.kwargs.get("title_id"),
            id=self.kwargs.get("review_id"),
        )
        new_queryset = review.comments.all()
        return new_queryset

    def perform_create(self, serializer):
        author = get_object_or_404(User, username=self.request.user)
        review = get_object_or_404(
            Review,
            title=self.kwargs.get("title_id"),
            id=self.kwargs.get("review_id"),
        )
        serializer.save(author=author, review=review)
