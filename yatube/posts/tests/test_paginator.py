from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post, User
from posts.tests.data_test_constants import INDEX_PAGE

POST_ON_PAGE_FIRST = 10
POST_ON_PAGE_SECOND = 3
POSTS_QUANTITY = POST_ON_PAGE_SECOND + POST_ON_PAGE_FIRST


class PostPaginatorViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(
            username='test_username'
        )
        cls.group = Group.objects.create(
            slug='test_slug',
        )
        test_posts = []
        number_of_post = 0
        for number_of_post in range(0, POSTS_QUANTITY):
            test_posts.append(Post(author=cls.user, group=cls.group))
            number_of_post += 1
        Post.objects.bulk_create(test_posts)
        cls.GROUP_PAGE = reverse('posts:group_list', kwargs={
                                 'slug': cls.group.slug})
        cls.POST_PROFILE_PAGE = reverse('posts:profile', kwargs={
                                        'username': cls.user.username})

    def setUp(self):
        self.guest_client = Client()

    def test_paginator(self):
        """Паджинатор работает правильно."""
        context_views = {
            INDEX_PAGE: POST_ON_PAGE_FIRST,
            self.POST_PROFILE_PAGE: POST_ON_PAGE_FIRST,
            self.GROUP_PAGE: POST_ON_PAGE_FIRST,
        }
        for reverse_name, quantity in context_views.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.guest_client.get(reverse_name)
                self.assertEqual(len(response.context['page_obj']), quantity)
        context_views = {
            INDEX_PAGE + '?page=2': POST_ON_PAGE_SECOND,
            self.POST_PROFILE_PAGE + '?page=2': POST_ON_PAGE_SECOND,
            self.GROUP_PAGE + '?page=2': POST_ON_PAGE_SECOND,
        }
        for reverse_name, quantity in context_views.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.guest_client.get(reverse_name)
                self.assertEqual(len(response.context['page_obj']), quantity)
