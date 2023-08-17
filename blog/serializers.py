from django.contrib.auth import get_user_model
from rest_framework import serializers

from blog.models import Post, Comment


class CommentSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Comment
        fields = ["user", "post", "text", "is_published", "created_at", "updated_at"]
        read_only_fields = ["user", "post", "is_published"]


#  POSTS
class PostSerializer(serializers.HyperlinkedModelSerializer):
    is_published = serializers.BooleanField(default=True)
    comments_amount = serializers.IntegerField(source="comment_set.count", read_only=True)

    class Meta:
        model = Post
        fields = [
            "user",
            "url",
            "id",
            "is_published",
            "title",
            "description",
            "created_at",
            "updated_at",
            "comments_amount",
        ]
        read_only_fields = ["user", "url", "comment_url"]


class PostCommentsSerializer(serializers.HyperlinkedModelSerializer):
    post_pk = serializers.PrimaryKeyRelatedField(read_only=True)
    user = serializers.HyperlinkedRelatedField(
        view_name="user-detail",
        lookup_field="pk",
        read_only=True,
    )

    class Meta:
        model = Comment
        fields = ["user", "post_pk", "text", "created_at"]


class PostDetailSerializer(serializers.HyperlinkedModelSerializer):
    is_published = serializers.BooleanField(default=True)
    comment_url = serializers.HyperlinkedRelatedField(
        view_name="comment-detail",
        lookup_field="pk",
        read_only=True,
    )
    comment_set = PostCommentsSerializer(many=True, read_only=True)

    class Meta:
        model = Post
        fields = [
            "user",
            "url",
            "comment_url",
            "id",
            "is_published",
            "title",
            "description",
            "created_at",
            "updated_at",
            "comment_set",
        ]
        read_only_fields = ["id", "url", "created_at", "updated_at"]


#  USERS
class UserPostsSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Post
        fields = ["url", "title", "created_at", "updated_at"]


class UserCommentsSerializer(serializers.HyperlinkedModelSerializer):
    post_pk = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Comment
        fields = ["post_pk", "text", "created_at"]


class UserSerializer(serializers.HyperlinkedModelSerializer):
    comments_amount = serializers.IntegerField(source="comment_set.count", read_only=True)
    posts_amount = serializers.IntegerField(source="post_set.count", read_only=True)

    class Meta:
        model = get_user_model()
        fields = ["url", "id", "username", "email", "comments_amount", "posts_amount"]


class UserDetailSerializer(serializers.HyperlinkedModelSerializer):
    post_set = UserPostsSerializer(many=True)
    comment_set = UserCommentsSerializer(many=True, read_only=True)

    class Meta:
        model = get_user_model()
        fields = ["url", "id", "username", "comment_set", "post_set"]
