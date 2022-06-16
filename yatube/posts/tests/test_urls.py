from http import HTTPStatus

from django.core.cache import cache
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post, User

INDEX_PAGE = reverse('posts:index')
POST_CREATE_PAGE = reverse('posts:post_create')
FOLLOWING_PAGE = reverse('posts:follow_index')


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(
            username='test_username'
        )
        cls.group = Group.objects.create(
            slug='test_slug',
        )
        cls.post = Post.objects.create(
            author=cls.user,
        )
        cls.GROUP_PAGE = reverse('posts:group_list', kwargs={
                                 'slug': cls.group.slug})
        cls.POST_EDIT_PAGE = reverse('posts:post_edit', kwargs={
                                     'post_id': cls.post.pk})
        cls.POST_DETAIL_PAGE = reverse('posts:post_detail', kwargs={
                                       'post_id': cls.post.pk})
        cls.POST_PROFILE_PAGE = reverse('posts:profile', kwargs={
                                        'username': cls.user.username})
        cls.ADD_COMMENT = reverse('posts:add_comment', kwargs={
                                  'post_id': cls.post.pk})

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def tearDown(self):
        cache.clear()

    def test_urls_at_desired_location_everybody(self):
        """"Страницы доступны любому пользователю."""
        url_names = [
            INDEX_PAGE,
            self.GROUP_PAGE,
            self.POST_DETAIL_PAGE,
            self.POST_PROFILE_PAGE,
        ]
        for address in url_names:
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK)
    
    def test_urls_at_desired_location_for_authorized_client(self):
        """"Страницы доступны любому пользователю."""
        response = self.authorized_client.get(POST_CREATE_PAGE)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_unexisting_page_not_found(self):
        """"Старница unexisting_page недоступна
        и об этом отображается соответствующий шаблон."""
        response = self.client.get('/unexisting_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertTemplateUsed(response, 'core/404.html')

    def test_urls_redirect(self):
        """"Для страниц создания комментария, редактирования
        и создания поста используются необходимые редиректы."""
        url_names = [
            POST_CREATE_PAGE,
            self.POST_EDIT_PAGE,
            self.ADD_COMMENT,
        ]
        for address in url_names:
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.FOUND)
        user = User.objects.create_user(username='unexist_test_username')
        self.authorized_client.force_login(user)
        response = self.authorized_client.get(self.POST_EDIT_PAGE)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_urls_use_correct_templates(self):
        """URL-адреса используют соответствующие шаблоны."""
        templates_url_names = {
            INDEX_PAGE: 'posts/index.html',
            self.GROUP_PAGE: 'posts/group_list.html',
            self.POST_PROFILE_PAGE: 'posts/profile.html',
            self.POST_DETAIL_PAGE: 'posts/post_detail.html',
            POST_CREATE_PAGE: 'posts/create_post.html',
            self.POST_EDIT_PAGE: 'posts/create_post.html',
        }
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)
