from rest_framework import mixins, viewsets


class MixinForMainModels(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    """
    Mixin для основных моделей.
    """

    pass
