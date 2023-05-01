from django import forms
from django.forms import ModelForm
from .models import Post, Comment


class PostForm(ModelForm):
    class Meta:
        model = Post
        fields = ['group', 'text', 'image']  # group has blank=True, so required is set to False


class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ['text']
