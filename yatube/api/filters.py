from django_filters import rest_framework as filters
from posts.models import Post


# find all posts with pub_date >= date_from and pub_date <= date_to
class PostFilter(filters.FilterSet):
    date_from = filters.DateTimeFilter(field_name='pub_date', lookup_expr='gte')
    date_to = filters.DateTimeFilter(field_name='pub_date', lookup_expr='lte')

    class Meta:
        model = Post
        fields = ['date_from', 'date_to']

