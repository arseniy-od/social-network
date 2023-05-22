import os
import tempfile
from PIL import Image

from django.test import TestCase, Client, override_settings
from django.core.cache import cache
from django.shortcuts import reverse
from django.conf import settings
from django.http import Http404

from .models import User, Post, Group, Follow
from .factories import GroupFactory


class TestPosts(TestCase):
    def setUp(self) -> None:
        self.auth_client = Client()
        self.anonymous_client = Client()
        self.user = User.objects.create_user(username='arthur', email='king_arthur@gmail.com', password="12345")
        self.group = GroupFactory()
        self.auth_client.login(username='arthur', password='12345')
        self.text = 'test text'

        cache.clear()

    def tearDown(self) -> None:
        Group.objects.filter(id=self.group.id).delete()
        User.objects.filter(id=self.user.id).delete()
        Post.objects.filter(text=self.text).delete()

    def test_profile_creation(self):
        # После регистрации пользователя создается его персональная страница (profile)
        profile_url = reverse('profile', args=(self.user.username,))
        response = self.auth_client.get(profile_url)
        self.assertEqual(response.status_code, 200)

    def test_new_post_page_get(self):
        response = self.auth_client.get(reverse('new_post'))
        self.assertEqual(response.status_code, 200)

    def test_post_creation(self):
        # Авторизованный пользователь может опубликовать пост (new)
        self.create_with_post_method(client=self.auth_client)
        post = Post.objects.get(text=self.text, group=self.group)
        self.assertIsNotNone(post)

    def create_with_post_method(self, client):
        client.post(reverse('new_post'), {'text': self.text, 'group': self.group.id})

    def test_unauthorized_creation(self):
        # Неавторизованный посетитель не может опубликовать пост (его редиректит на страницу входа)
        response = self.anonymous_client.get(reverse('new_post'), follow=True)
        self.assertEqual(response.resolver_match.url_name, 'login')

    def test_post_availability(self):
        # После публикации поста новая запись появляется на главной странице сайта (index),
        # на персональной странице пользователя (profile),
        # и на отдельной странице поста (post)
        self.create_with_post_method(client=self.auth_client)
        post_db = Post.objects.get(text=self.text)
        self.check_correspondence(post_db)

    def check_correspondence(self, post_db):
        for url in [reverse('index'),
                    reverse('profile', args=(self.user.username,)),
                    reverse('post', args=(self.user.username, post_db.id,))
                    ]:
            response = self.auth_client.get(url)
            if 'paginator' in response.context:
                post = response.context["page_obj"][0]
            else:
                post = response.context["post"]
            self.assertEqual(post, post_db)

    def test_edit(self):
        # Авторизованный пользователь может отредактировать свой пост
        # и его содержимое изменится на всех связанных страницах
        self.create_with_post_method(client=self.auth_client)
        post_id = Post.objects.get(text=self.text).id
        url = reverse('post_edit', args=(self.user.username, post_id))
        self.auth_client.post(url, {'text': 'I am still the king!', 'group': ''})
        post_db = Post.objects.get(text='I am still the king!')
        self.check_correspondence(post_db)

    def test_404(self):
        self.auth_client.get('/some-random-url-fadnsf3248sfkskdfsl/')  # used random symbols to create non-existing url
        self.assertRaises(Http404)


class TestFilesUpload(TestCase):
    def setUp(self) -> None:
        self.client = Client()
        self.group = Group.objects.create(title='Test group', slug='test-group')
        self.user = User.objects.create_user(username='test_user', email='test@gmail.com', password="12345")
        self.client.login(username='test_user', password='12345')
        self.client.post(reverse('new_post'), {'text': 'Test message without image', 'group': self.group.id})
        cache.clear()

    def test_post_with_tmp_image(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            with override_settings(MEDIA_ROOT=tmp_dir):
                self.post_image()
                self.check_image_availability()

    def post_image(self):
        image = Image.new(mode='RGB', size=(1000, 1000), color=(256, 0, 0))
        tmp_file = tempfile.NamedTemporaryFile(suffix='.png')
        with tmp_file as fp:
            image.save(fp, format='png')
            fp.seek(0)
            url = reverse('post_edit', kwargs={'username': self.user.username, 'pk': 1})
            response = self.client.post(url,
                                        {'author': self.user,
                                         'text': 'post with image',
                                         'group': self.group.id,
                                         'image': fp})

        post = Post.objects.get(text='post with image')
        params = {'username': self.user.username, 'pk': post.id}
        self.assertRedirects(response,
                             expected_url=reverse('post', kwargs=params),
                             msg_prefix=f"You should be redirected. Status code: {response.status_code}, not 302")

    def check_image_availability(self):
        urls = [reverse('index'),
                reverse('profile', kwargs={'username': self.user.username}),
                reverse('post', kwargs={'username': self.user.username, 'pk': 1}),
                reverse('group_posts', kwargs={'slug': self.group.slug}),
                ]
        for url in urls:
            cache.clear()
            page = self.client.get(url)
            self.assertContains(page, '<img', msg_prefix=f'img not found at {url}')

    def test_non_graphic_format(self):
        with tempfile.TemporaryFile() as fp:
            fp.write(b'Hello world!')
            fp.seek(0)
            url = reverse('post_edit', kwargs={'username': self.user.username, 'pk': 1})
            response = self.client.post(url,
                                        {'author': self.user,
                                         'text': 'post with image',
                                         'group': self.group.id,
                                         'image': fp})

        self.assertEqual(response.resolver_match.url_name, 'post_edit')
        self.assertContains(response, 'alert')


class TestCache(TestCase):
    def setUp(self) -> None:
        self.client = Client()
        self.group = Group.objects.create(title='Test group', slug='test-group')
        self.user = User.objects.create_user(username='test_user', email='test@gmail.com', password="12345")
        self.client.login(username='test_user', password='12345')

    def test_cache(self):
        response1 = self.client.get('')
        self.client.post('/new/', {'text': 'Test message', 'group': self.group.id})
        response2 = self.client.get('')
        cache.clear()
        response3 = self.client.get('')

        self.assertEqual(response1.content, response2.content, msg='Page is not cached')
        self.assertNotEqual(response1.content, response3.content,
                            msg='After clearing cache, page should change (new post added)')


class TestFollows(TestCase):
    def setUp(self) -> None:
        self.client = Client()
        self.group = Group.objects.create(title='Test group', slug='test-group')
        self.user1 = User.objects.create_user(username='test_user1', email='test1@gmail.com', password="12345")
        self.user2 = User.objects.create_user(username='test_user2', email='test2@gmail.com', password="12345")
        self.user3 = User.objects.create_user(username='test_user3', email='test3@gmail.com', password="12345")
        self.client.login(username='test_user1', password='12345')
        cache.clear()

    def test_follow_unfollow(self):
        self.client.login(username='test_user1', password='12345')

        # check that user1 is not following user2
        self.assertFalse(Follow.objects.filter(user=self.user1, author=self.user2).exists())
        self.follow(self.user2)
        # check that user1 is following user2
        self.assertTrue(Follow.objects.filter(user=self.user1, author=self.user2).exists())
        self.unfollow(self.user2)
        # check that user1 is not following user2
        self.assertFalse(Follow.objects.filter(user=self.user1, author=self.user2).exists())

    def follow(self, user):
        url = reverse('profile_follow', args=(user.username,))
        self.client.get(url)

    def unfollow(self, user):
        url = reverse('profile_unfollow', args=(user.username,))
        self.client.get(url)

    def test_post_in_follow(self):
        self.follow(self.user2)
        post_db = Post.objects.create(text="Test post", author=self.user2)
        self.assertTrue(self.check_post_in_follow(post_db))
        self.unfollow(self.user2)
        self.assertFalse(self.check_post_in_follow(post_db))

    def check_post_in_follow(self, post_db):
        cache.clear()
        response = self.client.get(reverse('follow_index'))
        if 'paginator' in response.context:
            post_list = response.context.get("page_obj")
            post = post_list[0] if post_list else None
        else:
            post = response.context.get("post", None)
        return post == post_db

    def test_authorized_comments(self):
        post_db = Post.objects.create(text="Test post", author=self.user2)
        comment_url = reverse('add_comment', kwargs={'username': self.user2.username,
                                                     'pk': post_db.id})
        response = self.client.post(comment_url, {'text': 'authorized comment'}, follow=True)
        self.assertContains(response, 'authorized comment')

        self.client.logout()
        self.client.post(comment_url, {'text': 'unauthorized comment'})
        post_url = reverse('post', kwargs={'username': self.user2.username,
                                           'pk': post_db.id})
        response = self.client.get(post_url)
        self.assertNotContains(response, 'unauthorized comment')

