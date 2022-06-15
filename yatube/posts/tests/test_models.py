from django.test import TestCase

from posts.models import Group, Post, User

FIRST_LETTERS = 15


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(
            username='test_name'
        )
        cls.group = Group.objects.create(
            title='Тестовое наименование группы',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый текст поста',
        )

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""
        group = PostModelTest.group
        expected_object_group_name = group.title
        self.assertEqual(expected_object_group_name, str(group))
        post = PostModelTest.post
        expected_object_post_name = post.text[:FIRST_LETTERS]
        self.assertEqual(expected_object_post_name, str(post))
