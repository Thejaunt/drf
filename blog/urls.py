from django.urls import path, include
from rest_framework.routers import DefaultRouter

from blog.views import PostViewSet, UserViewSet


router = DefaultRouter()
router.register(r"-posts", PostViewSet, basename="post")
router.register("-users", UserViewSet, basename="user")

urlpatterns = [
    path("blog", include(router.urls)),
]
