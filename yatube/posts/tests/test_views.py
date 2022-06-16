import shutil

from django.core.cache import cache
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from posts.forms import PostForm
from posts.models import Follow, Group, Post, User
from posts.tests.data_test_constants import (FOLLOWING_PAGE, IMAGE, INDEX_PAGE,
                                             POST_CREATE_PAGE, TEMP_MEDIA_ROOT)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(
            username='username'
        )
        cls.second_user = User.objects.create_user(
            username='second_test_username'
        )
        cls.third_user = User.objects.create_user(
            username='third_test_username'
        )
        cls.group = Group.objects.create(
            slug='group_slug',
        )
        cls.another_group = Group.objects.create(
            slug='yet_another_slug'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            group=cls.group,
            text='Текст поста',
            image=IMAGE,
        )
        cls.GROUP_PAGE = reverse('posts:group_list', kwargs={
                                 'slug': cls.group.slug})
        cls.ANOTHER_GROUP_PAGE = reverse('posts:group_list', kwargs={
            'slug': cls.another_group.slug})
        cls.POST_EDIT_PAGE = reverse('posts:post_edit', kwargs={
            'post_id': cls.post.pk})
        cls.POST_DETAIL_PAGE = reverse('posts:post_detail', kwargs={
            'post_id': cls.post.pk})
        cls.POST_PROFILE_PAGE = reverse('posts:profile', kwargs={
            'username': cls.user.username})
        cls.FOLLOWING_POST_PROFILE_PAGE = reverse('posts:profile', kwargs={
            'username': cls.second_user.username})
        cls.FOLLOW = reverse('posts:profile_follow', kwargs={
            'username': cls.second_user.username})
        cls.UNFOLLOW = reverse('posts:profile_unfollow', kwargs={
            'username': cls.second_user.username})

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.second_authorized_client = Client()
        self.second_authorized_client.force_login(self.third_user)

    def tearDown(self):
        cache.clear()

    def test_view_function_show_correct_context(self):
        """View-функции передают ожидаемый словарь context."""
        context_views = (
            (INDEX_PAGE, self.post),
            (self.POST_PROFILE_PAGE, self.post),
            (self.GROUP_PAGE, self.post),
        )
        for reverse_name, context in context_views.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertEqual(response.context['page_obj'][0], context)
        response = self.authorized_client.get(self.POST_DETAIL_PAGE)
        self.assertEqual(response.context['post'], self.post)
        cache.clear()

    def test_view_function_show_correct_context(self):
        """View-функции создания и редактирования поста
        передают ожидаемый словарь context."""
        context_views = {
            POST_CREATE_PAGE: PostForm,
            self.POST_EDIT_PAGE: PostForm,
        }
        for reverse_name, context in context_views.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertIsInstance(response.context.get('form'), context)

    def test_view_function_show_correct_context(self):
        """Словарь context view-функций содержит ожидаемые значения"""
        context_views = [
            INDEX_PAGE,
            self.GROUP_PAGE,
            self.POST_PROFILE_PAGE,
            self.POST_DETAIL_PAGE,
        ]
        for reverse_name in context_views:
            with self.subTest(reverse_name=reverse_name):
                response = self.guest_client.get(reverse_name)
                self.assertEqual(response.context.get(
                    'post').author, self.user)
                self.assertEqual(response.context.get(
                    'post').group, self.group)
                self.assertNotEqual(response.context.get(
                    'post').group, self.another_group)
                self.assertEqual(response.context.get(
                    'post').text, self.post.text)
                self.assertEqual(response.context.get(
                    'post').image, self.post.image)

    def test_cache_index_page(self):
        """Проверка работы кэша в index_page"""
        new_post = Post.objects.create(author=self.user, text='text')
        first_request_content = self.guest_client.get(INDEX_PAGE).content
        new_post.delete()
        second_request_content = self.guest_client.get(INDEX_PAGE).content
        self.assertEqual(first_request_content, second_request_content)
        cache.clear()
        third_request_content = self.guest_client.get(INDEX_PAGE).content
        self.assertNotEqual(second_request_content, third_request_content)

    def test_following(self):
        """Сервис подписок и отписок работает корректно"""
        second_post = Post.objects.create(
            author=self.second_user,
            text='Текст поста второго пользователя',
        )

        following_quantity = Follow.objects.count()
        response = self.authorized_client.post(self.FOLLOW)
        self.assertTrue(Follow.objects.filter(
            user=self.user,
            author=self.second_user,
        ).exists())
        self.assertEqual(Follow.objects.count(), following_quantity + 1)
        self.assertRedirects(response, self.FOLLOWING_POST_PROFILE_PAGE)

        response = self.authorized_client.get(FOLLOWING_PAGE)
        self.assertEqual(response.context.get('post'), second_post)

        response = self.second_authorized_client.get(FOLLOWING_PAGE)
        self.assertNotEqual(response.context.get('post'), second_post)

    def test_unfollowing(self):
        second_post = Post.objects.create(
            author=self.second_user,
            text='Текст поста второго пользователя',
        )
        Follow.objects.create(
            author=self.second_user,
            user=self.user,
        )
        following_quantity = Follow.objects.count()
        response = self.authorized_client.post(self.UNFOLLOW)

        self.assertEqual(Follow.objects.count(), following_quantity - 1)
        self.assertFalse(Follow.objects.filter(
            user=self.user,
            author=self.second_user,
        ).exists())
        response = self.authorized_client.get(FOLLOWING_PAGE)
        self.assertNotEqual(response.context.get('post'), second_post)
