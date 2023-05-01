from rest_framework import serializers
from posts.models import Post, Comment, User


class PostSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source='author.username')
    comments = serializers.SerializerMethodField()

    def get_comments(self, obj):
        post = Post.objects.get(id=obj.pk)
        comments = Comment.objects.filter(post=post)
        return [comment.text for comment in comments]

    class Meta:
        model = Post
        fields = ['id', 'text', 'author', 'image', 'pub_date', 'comments']


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source='author.username')
    post = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'author', 'post', 'text', 'created']
