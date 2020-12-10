import shutil
import tempfile
from django import forms
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings
from django.test import Client, TestCase
from django.urls import reverse

from posts.forms import PostForm
from posts.models import Comment, Follow, Group, Post, User

SLUG = 'test-slug'
USER = 'VasyaPupkin'
USER2 = 'PupaVaskin'
INDEX_URL = reverse('index')
NEW_POST_URL = reverse('new_post')

CONTENT_TYPE = 'image/gif'
SMALL_PIC = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B')


class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        settings.MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
        cls.user = User.objects.create(username=USER)
        cls.user2 = User.objects.create(username=USER2)
        cls.form = PostForm()
        cls.authorized_client = Client()
        cls.authorized_client2 = Client()
        cls.authorized_client.force_login(cls.user)
        cls.authorized_client2.force_login(cls.user2)
        cls.group = Group.objects.create(
            title='Тестовая группа',
            description='Описание',
            slug=SLUG)
        cls.FOLLOW_URL = reverse('profile_follow', args=[USER2])
        cls.UNFOLLOW_URL = reverse('profile_unfollow', args=[USER2])

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.post = Post.objects.create(
            text='Тестовый текст',
            author=self.user,
            )
        self.EDIT_POST_URL = reverse('post_edit', args=[USER, self.post.id])
        self.VIEW_POST_URL = reverse('post', args=[USER, self.post.id])
        self.NEW_COMMENT_URL = reverse(
            'add_comment',
            args=[USER, self.post.id]
            )

    def test_create_post(self):
        """Валидная форма создает запись в Post."""
        self.post.delete()
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=SMALL_PIC,
            content_type=CONTENT_TYPE
        )
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Тестовый текст 2',
            'group': self.group.id,
            'image': uploaded,
            }
        response = self.authorized_client.post(
            NEW_POST_URL,
            data=form_data,
            follow=True
            )
        post = response.context['page'][0]
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertEqual(post.text, form_data['text'])
        self.assertEqual(post.group.id, form_data['group'])
        self.assertEqual(post.image.size, form_data['image'].size)
        self.assertEqual(post.author, self.user)
        self.assertRedirects(response, INDEX_URL)

    def test_create_comment(self):
        """Валидная форма создает комментарий."""
        comments_count = Comment.objects.count()
        form_data = {
            'text': 'Комментарий',
            'post': self.post
            }
        response = self.authorized_client.post(
            self.NEW_COMMENT_URL,
            data=form_data,
            follow=True
            )
        comment = response.context['comments'][0]
        self.assertEqual(comment.text, form_data['text'])
        self.assertEqual(comment.post, form_data['post'])
        self.assertEqual(Comment.objects.count(), comments_count + 1)
        self.assertRedirects(response, self.VIEW_POST_URL)

    def test_edit_post(self):
        """Валидная форма редактирует запись в Post."""
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=SMALL_PIC,
            content_type=CONTENT_TYPE
        )
        form_data = {
            'text': 'Тестовый текст 2',
            'group': self.group.id,
            'image': uploaded,
            }
        posts_count = Post.objects.count()
        response = self.authorized_client.post(
            self.EDIT_POST_URL,
            data=form_data,
            follow=True
            )
        post = response.context.get('post')
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertEqual(post.text, form_data['text'])
        self.assertEqual(post.group.id, form_data['group'])
        self.assertEqual(post.image.size, form_data['image'].size)
        self.assertRedirects(response, self.VIEW_POST_URL)

    def test_new_post_pages_show_correct_context(self):
        """Шаблон new_post сформирован с правильным контекстом."""
        response = self.authorized_client.get(NEW_POST_URL)
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
            'image': forms.fields.ImageField
        }
        form = response.context.get('form')
        for value, expected in form_fields.items():
            with self.subTest():
                form_field = form.fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_authorized_client_can_subscribe_to_other_users(self):
        """Авторизованный пользователь может подписаться
        на других пользователей."""
        count = Follow.objects.count()
        self.authorized_client.get(self.FOLLOW_URL)
        follow = Follow.objects.get(user=self.user)
        self.assertEqual(count+1, Follow.objects.count())
        self.assertEqual(follow.author, self.user2)

    def test_authorized_client_can_unsubscribe_to_other_users(self):
        """Авторизованный пользователь может отписываться
        от других пользователей."""
        count = Follow.objects.count()
        Follow.objects.create(user=self.user, author=self.user2)
        self.assertEqual(count+1, Follow.objects.count())
        self.authorized_client.post(self.UNFOLLOW_URL)
        self.assertEqual(count, Follow.objects.count())
