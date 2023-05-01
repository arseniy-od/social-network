from django.urls import path, include

from rest_framework.authtoken import views as auth_views
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register('posts', views.PostViewSet)
router.register('posts/(?P<id>[0-9]+)/comments', views.CommentViewSet)


urlpatterns = [
    path('api-token-auth/', auth_views.obtain_auth_token),
    path('', include(router.urls)),
]
