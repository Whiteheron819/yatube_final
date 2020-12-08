from django.test import TestCase

from posts.models import Group, Post, User


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(
            username='testsubject',
            email='testsubject@gmail.com',
            password='qwerty47')
        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=cls.user,
            )

    def test_post_verbose_name(self):
        """verbose_name в полях совпадает с ожидаемым."""
        post = self.post
        field_verboses = {'text': 'Текст'}
        for value, expected in field_verboses.items():
            with self.subTest():
                self.assertEqual(
                    post._meta.get_field(value).verbose_name, expected)

    def test_post_name_is_title_fild(self):
        """В поле __str__  объекта post записано значение поля post.text,
        post.author, post.pub_date и post.group."""
        post = PostModelTest.post
        expected_object_name = (f'{post.text[:15]} {post.author} '
                                f'{post.pub_date} {post.group}')
        self.assertEquals(expected_object_name, str(post))

    def test_help_text(self):
        """help_text в полях совпадает с ожидаемым."""
        post = PostModelTest.post
        field_help_texts = {
            'text': 'Поле для сообщения',
            'group': 'Выбор сообщества'
        }
        for value, expected in field_help_texts.items():
            with self.subTest():
                self.assertEqual(
                    post._meta.get_field(value).help_text, expected)


class GroupModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Тестовая группа',
            description='Описание',
            slug='test-slug')

    def test_group_verbose_name(self):
        """verbose_name в полях совпадает с ожидаемым."""
        group = GroupModelTest.group
        field_verboses = {'title': 'Заголовок'}
        for value, expected in field_verboses.items():
            with self.subTest():
                self.assertEqual(
                    group._meta.get_field(value).verbose_name, expected)

    def test_group_name_is_title_fild(self):
        """В поле __str__  объекта group записано значение поля group.title."""
        group = GroupModelTest.group
        expected_object_name = group.title
        self.assertEquals(expected_object_name, str(group))

    def test_help_text(self):
        """help_text в полях совпадает с ожидаемым."""
        post = GroupModelTest.group
        field_help_texts = {
            'title': 'Название группы',
        }
        for value, expected in field_help_texts.items():
            with self.subTest():
                self.assertEqual(
                    post._meta.get_field(value).help_text, expected)
