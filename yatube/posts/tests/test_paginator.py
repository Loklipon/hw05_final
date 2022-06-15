from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post, User
from posts.tests.test_urls import INDEX_PAGE

POST_ON_PAGE_FIRST = 10
POST_ON_PAGE_SECOND = 3
POSTS_QUANTITY = 13


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
        number_of_post = 0
        for number_of_post in range(0, POSTS_QUANTITY):
            Post.objects.create(author=cls.user, group=cls.group)
            number_of_post += 1
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