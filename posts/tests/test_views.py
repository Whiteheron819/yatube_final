import shutil
import tempfile
from django.conf import settings
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Follow, Group, Post, User

USER = 'VasyaPupkin'
USER2 = 'PupaVaskin'
SLUG = 'test-slug'
SLUG2 = 'second-slug'
GROUP_POST_URL = reverse('group_posts', args=[SLUG])
GROUP2_POST_URL = reverse('group_posts', args=[SLUG2])
INDEX_URL = reverse('index')
NEW_POST_URL = reverse('new_post')
USER_URL = reverse('profile', args=[USER])
FOLLOW_INDEX_URL = reverse('follow_index')

CONTENT_TYPE = 'image/gif'
SMALL_PIC = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B')


class PostViewTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        settings.MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
        cls.user = User.objects.create(username=USER)
        cls.user2 = User.objects.create(username=USER2)
        cls.group = Group.objects.create(
            title='Тестовая группа',
            description='Описание',
            slug=SLUG)
        cls.second_group = Group.objects.create(
            title='Вторая группа',
            description='Описание',
            slug=SLUG2)
        cls.guest_client = Client()
        cls.authorized_client = Client()
        cls.authorized_client2 = Client()
        cls.authorized_client.force_login(cls.user)
        cls.authorized_client2.force_login(cls.user2)
        cls.follow = Follow.objects.create(
            user=cls.user,
            author=cls.user2)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=SMALL_PIC,
            content_type=CONTENT_TYPE
        )
        self.post = Post.objects.create(
            text='Тестовый текст',
            author=self.user,
            group=self.group,
            image=uploaded,
            )
        self.post2 = Post.objects.create(
            text='Тестовый текст 2',
            author=self.user2)
        self.EDIT_POST_URL = reverse('post_edit', args=[USER, self.post.id])
        self.VIEW_POST_URL = reverse('post', args=[USER, self.post.id])

    def test_post_show_correct_context(self):
        """Шаблон post сформирован с правильным контекстом."""
        response = self.guest_client.get(self.VIEW_POST_URL)
        post = response.context.get('post')
        self.assertEqual(post, self.post)

    def test_group_posts_in_correct_groups(self):
        """Пост не появляется на странице другой группы"""
        response = self.guest_client.get(GROUP2_POST_URL)
        post = response.context.get('page')
        self.assertNotIn(self.post, post)

    def test_correct_post_show_in_follow_index(self):
        """Пост автора, на которого ты подписан
           появляется на странице подписок"""
        response = self.authorized_client.get(FOLLOW_INDEX_URL)
        post = response.context.get('page')[0]
        self.assertEqual(self.post2, post)

    def test_unsubscribe_post_not_show_in_follow_index(self):
        """Пост автора, на которого ты не подписан
           не появляется на странице подписок"""
        response = self.authorized_client2.get(FOLLOW_INDEX_URL)
        post = response.context.get('page')
        self.assertNotIn(self.post, post)

    def test_context_with_post_show_correct_context(self):
        """Шаблоны сформированы с правильным контекстом."""
        self.post2.delete()
        cache.clear()
        urls = (
            INDEX_URL,
            USER_URL,
            GROUP_POST_URL,
        )
        for url in urls:
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                post = response.context.get('page')[0]
                self.assertEqual(post, self.post)
