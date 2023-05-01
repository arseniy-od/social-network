from django.urls import path
from django.views.decorators.cache import cache_page
from rest_framework.authtoken import views as auth_views


from . import views

urlpatterns = [
    path('',
         cache_page(5, key_prefix='index_page')(
             views.PostListView.as_view()
         ),
         name='index'),
    path('group/<slug:slug>/', views.GroupPostsView.as_view(), name='group_posts'),
    path('new/', views.CreatePostView.as_view(), name='new_post'),
    path('404/', views.page_not_found, {'exception': None}, name='404'),
    path('500/', views.server_error, name='500'),
    path('follow/', views.FollowPostsView.as_view(), name='follow_index'),
]


# profile
urlpatterns += [
    path('user/<str:username>/follow/', views.profile_follow, name='profile_follow'),
    path('user/<str:username>/unfollow/', views.profile_unfollow, name='profile_unfollow'),
    path('user/<str:username>/', views.ProfileView.as_view(), name='profile'),
    path('user/<str:username>/<int:pk>/', views.PostDetail.as_view(), name='post'),
    path('user/<str:username>/<int:pk>/edit/', views.PostEditView.as_view(), name='post_edit'),
    path('user/<str:username>/<int:pk>/delete/', views.PostDeleteView.as_view(), name='post_delete'),
    path('user/<str:username>/<int:pk>/comment', views.AddCommentView.as_view(), name='add_comment'),
]