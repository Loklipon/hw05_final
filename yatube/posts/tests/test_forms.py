import shutil

from django.test import Client, TestCase, override_settings
from django.urls import reverse

from posts.models import Comment, Group, Post, User
from posts.tests.test_urls import POST_CREATE_PAGE
from posts.tests.test_views import IMAGE, TEMP_MEDIA_ROOT


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(
            username='test_username'
        )
        cls.group = Group.objects.create(
        )
        cls.post = Post.objects.create(
            author=cls.user,
            group=cls.group,
            text='Текст',
        )
        cls.POST_EDIT_PAGE = reverse('posts:post_edit', kwargs={
                                     'post_id': cls.post.pk})
        cls.POST_DETAIL_PAGE = reverse('posts:post_detail', kwargs={
                                       'post_id': cls.post.pk})
        cls.POST_PROFILE_PAGE = reverse('posts:profile', kwargs={
                                        'username': cls.user.username})

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post(self):
        """Валидная форма создает новый пост в Post."""
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Тестовый текст',
            'group': self.group.pk,
            'image': IMAGE,
        }
        response = self.authorized_client.post(
            POST_CREATE_PAGE,
            data=form_data,
        )
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(Post.objects.filter(
            text='Тестовый текст',
            group=self.group,
            author=self.user,
            image='posts/picture.png',
        ).exists())
        self.assertRedirects(response, self.POST_PROFILE_PAGE)

    def test_edit_post(self):
        """Валидная форма изменяет существующий пост в Post."""
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Новый тестовый текст',
        }
        response = self.authorized_client.post(
            self.POST_EDIT_PAGE,
            data=form_data
        )
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertTrue(Post.objects.filter(
            text='Новый тестовый текст').exists())
        self.assertFalse(Post.objects.filter(text=self.post.text).exists())
        self.assertRedirects(response, self.POST_DETAIL_PAGE)


class CommentFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(
            username='test_username'
        )
        cls.group = Group.objects.create(
        )
        cls.post = Post.objects.create(
            author=cls.user,
            group=cls.group,
        )
        cls.comment = Comment.objects.create(
            post=cls.post,
            author=cls.user,
            text='Текст первого комментария',
        )
        cls.ADD_COMMENT = reverse('posts:add_comment', kwargs={
                                  'post_id': cls.post.pk})
        cls.POST_DETAIL_PAGE = reverse('posts:post_detail', kwargs={
                                       'post_id': cls.post.pk})

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_and_delete_comment(self):
        """Валидная форма создает новый комментарий в Comment"""
        comment_count = Comment.objects.count()
        form_data = {
            'text': 'Текст второго комментария',
            'author': self.user,
            'post': self.post.pk,
        }
        self.authorized_client.post(
            self.ADD_COMMENT,
            data=form_data,
        )
        self.assertEqual(Comment.objects.count(), comment_count + 1)
        self.assertTrue(Comment.objects.filter(
            text='Текст второго комментария',
            author=self.user,
            post=self.post,
        ).exists())
