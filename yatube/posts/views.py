import requests
from django.shortcuts import render, get_object_or_404, redirect, reverse
from django.urls import reverse_lazy
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib import messages
from django.core.paginator import Paginator
from django.core.exceptions import PermissionDenied
from django.views.generic import (ListView,
                                  DetailView,
                                  CreateView,
                                  UpdateView,
                                  DeleteView,
                                  View
                                  )

from .models import Post, Group, User, Follow, Comment
from .forms import PostForm, CommentForm

POSTS_PER_PAGE = 5


class PostListView(ListView):
    model = Post
    paginate_by = 5
    template_name = 'index.html'


class GroupPostsView(ListView):
    paginate_by = 5
    template_name = 'group.html'

    def get_queryset(self):
        slug = self.kwargs.get("slug")
        group = get_object_or_404(Group, slug=slug)
        posts = Post.objects.select_related('author', 'group').filter(group=group).order_by('-pub_date')
        return posts


class ProfileView(ListView):
    paginate_by = 5
    template_name = 'profile.html'

    def get_author(self):
        username = self.kwargs.get('username')
        author = get_object_or_404(User, username=username)
        return author

    def get_queryset(self):
        author = self.get_author()
        posts = list(author.posts.select_related('group').order_by('-pub_date'))
        return posts

    @property
    def extra_context(self):
        author = self.get_author()
        subscribers = Follow.objects.filter(author=author).count()
        subscribed = Follow.objects.filter(user=author).count()
        user = self.request.user
        if user.is_authenticated:
            following = Follow.objects.filter(user=user, author=author).exists()
        else:
            following = False
        context = {'author': author,
                   'following': following,
                   'subscribers': subscribers,
                   'subscribed': subscribed}
        return context


class PostDetail(DetailView):
    model = Post
    template_name = 'post_detail.html'

    def get_author(self):
        username = self.kwargs.get('username')
        return get_object_or_404(User, username=username)

    @property
    def extra_context(self):
        author = self.get_author()
        subscribers = Follow.objects.filter(author=author).count()
        subscribed = Follow.objects.filter(user=author).count()
        return {'comment_form': CommentForm(),
                'author': author,
                'subscribers': subscribers,
                'subscribed': subscribed
                }


class PostEditView(LoginRequiredMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'new_post.html'
    extra_context = {'edit': True}

    def dispatch(self, request, *args, **kwargs):
        pk = self.kwargs.get('pk')
        post = get_object_or_404(Post, id=pk)
        if self.request.user != post.author:
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)


class CreatePostView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'new_post.html'
    extra_context = {'edit': False}

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class PostDeleteView(LoginRequiredMixin, DeleteView):
    model = Post
    template_name = 'post_delete.html'
    success_url = reverse_lazy('index')

    def dispatch(self, request, *args, **kwargs):
        pk = self.kwargs.get('pk')
        post = get_object_or_404(Post, id=pk)
        if self.request.user != post.author:
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        messages.add_message(
            self.request,
            messages.INFO,
            f'Post "{self.object.text:.15}{"..." if len(self.object.text) > 15 else ""}" deleted successfully')
        return super().get_context_data(**kwargs)


class AddCommentView(LoginRequiredMixin, CreateView):
    model = Comment
    form_class = CommentForm
    template_name = 'post_detail.html'

    def form_valid(self, form):
        post = get_object_or_404(Post, id=self.kwargs.get('pk'))
        form.instance.author = self.request.user
        form.instance.post = post
        return super().form_valid(form)


class FollowPostsView(LoginRequiredMixin, ListView):
    model = Post
    paginate_by = 5
    template_name = 'follow.html'

    def get_queryset(self):
        posts = Post.objects.filter(author__following__user=self.request.user).order_by('-pub_date')
        return posts


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    if not Follow.objects.filter(user=request.user, author=author).exists():
        Follow.objects.create(user=request.user, author=author)
    return redirect('profile', username=username)


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    follow = get_object_or_404(Follow, user=request.user, author=author)
    follow.delete()
    return redirect('profile', username=username)


# Error pages
def page_not_found(request, exception):
    return render(request, 'misc/404.html', {'path': request.path}, status=404)


def server_error(request):
    return render(request, 'misc/500.html', status=500)


