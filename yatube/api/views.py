from loguru import logger
from django.shortcuts import get_object_or_404

from rest_framework import generics, viewsets, status, filters, authentication
from rest_framework.permissions import IsAuthenticated

from django_filters.rest_framework import DjangoFilterBackend

from posts.models import Post, Comment
from .serializers import PostSerializer, CommentSerializer
from .permissions import IsAuthorOrReadOnly
from .filters import PostFilter


logger.add('debug.json', format="{time} {level} {message}",
           level="DEBUG", rotation="1 week", compression="zip",
           serialize=True)


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [
        IsAuthenticated,
        IsAuthorOrReadOnly,
    ]
    filter_backends = [DjangoFilterBackend]
    filterset_class = PostFilter
    ordering_fields = ['-pub_date', 'username']

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [
        IsAuthenticated,
        IsAuthorOrReadOnly,
    ]

    def get_post(self):
        return get_object_or_404(Post, id=self.kwargs.get('id'))

    def get_queryset(self):
        return Comment.objects.filter(post=self.get_post())

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, post=self.get_post())
