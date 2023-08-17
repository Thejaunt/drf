from django.contrib.auth import get_user_model
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

from blog.models import Post
from blog.serializers import (
    CommentSerializer,
    PostSerializer,
    UserSerializer,
    PostDetailSerializer,
    UserDetailSerializer,
)


from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from dj_rest_auth.registration.views import SocialLoginView

class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.user == request.user


class UserIsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.id == request.user.id


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.select_related("user").prefetch_related("comment_set")
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    serializer_class = PostSerializer

    def get_serializer_class(self):
        if self.action == "add_comment":
            return CommentSerializer
        if self.action == "retrieve":
            return PostDetailSerializer
        return self.serializer_class

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=["get", "post"])
    def add_comment(self, request, pk=None):
        post = self.get_object()
        serializer = self.get_serializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            serializer.save(user=request.user, post=post, is_published=True)
            return Response({"status": "comment added"})
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserViewSet(viewsets.ModelViewSet):
    queryset = get_user_model().objects.prefetch_related("post_set", "comment_set")
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, UserIsOwnerOrReadOnly]

    def retrieve(self, request, pk=None, **kwargs):
        post = get_object_or_404(self.queryset, pk=pk)
        serializer = UserDetailSerializer(post, context={"request": request})
        return Response(serializer.data)


class GoogleLogin(SocialLoginView):
    adapter_class = GoogleOAuth2Adapter
