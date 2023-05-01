from django.db import models
from django.contrib.auth import get_user_model
from django.urls import reverse

User = get_user_model()


class Group(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.title


class Post(models.Model):
    text = models.TextField()
    pub_date = models.DateTimeField("date published", auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="posts")
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name="posts", blank=True, null=True)
    image = models.ImageField(upload_to='posts/', blank=True, null=True)

    def get_absolute_url(self):
        return reverse('post', kwargs={'username': self.author.username, 'pk': self.pk})

    def __str__(self):
        return self.text

    class Meta:
        ordering = ('-pub_date',)


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    text = models.TextField()
    created = models.DateTimeField(auto_now_add=True)

    def get_absolute_url(self):
        return reverse('post', kwargs={'username': self.post.author.username, 'pk': self.post.pk})

    class Meta:
        ordering = ('created',)


class Follow(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='follower')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='following')

    def __str__(self):
        return f'User: {self.user} follows author: {self.author}'
