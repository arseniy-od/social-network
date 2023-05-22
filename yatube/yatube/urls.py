from django.contrib import admin
from django.urls import path, include
from django.contrib.flatpages import views
from django.conf.urls import handler404, handler500
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import authtoken


handler404 = 'posts.views.page_not_found'  # noqa
handler500 = 'posts.views.server_error'    # noqa

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('posts.urls')),
    path('auth/', include('users.urls')),
    path('auth/', include('django.contrib.auth.urls')),
    path('debug/', include('debug_toolbar.urls')),
    path('about/', include('django.contrib.flatpages.urls')),
    path('api/v1/', include('api.urls'))
]

# flatpages
urlpatterns += [
    path('about-us/', views.flatpage, {'url': '/about-us/'}, name='about'),
    path('terms/', views.flatpage, {'url': '/terms/'}, name='terms'),
    path('about-author/', views.flatpage, {'url': '/about-author/'}, name="about_author"),
    path('about-spec/', views.flatpage, {'url': '/about-spec/'}, name="about_spec"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
