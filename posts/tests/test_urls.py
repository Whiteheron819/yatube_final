from django.core.cache import cache
from django.contrib.flatpages.models import FlatPage
from django.contrib.sites.models import Site
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post, User

USER = 'VasyaPupkin'
USER2 = 'PupaVaskin'
SLUG = 'test-slug'
GROUP_POST_URL = reverse('group_posts', args=[SLUG])
INDEX_URL = reverse('index')
NEW_POST_URL = reverse('new_post')
AUTHOR_URL = reverse('author')
SPEC_URL = reverse('spec')
USER_URL = reverse('profile', args=[USER])
WRONG_USER_URL = reverse('profile', args=['NotCreatedUser'])


class PostsURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.site1 = Site(pk=1, domain='example.com', name='example.com')
        cls.site1.save()
        cls.group = Group.objects.create(
            title='Тестовая группа',
            description='Описание',
            slug=SLUG)
        cls.guest_client = Client()
        cls.user = User.objects.create(username=USER)
        cls.user2 = User.objects.create(username=USER2)
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.authorized_client2 = Client()
        cls.authorized_client2.force_login(cls.user2)
        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=cls.user,
            group=cls.group,
            )
        cls.about_author = FlatPage.objects.create(
            url=AUTHOR_URL,
            title='about_author',
            content='its a about author content')
        cls.about_spec = FlatPage.objects.create(
            url=SPEC_URL,
            title='about_spec',
            content='its a about spec content')
        cls.about_author.sites.add(cls.site1)
        cls.about_spec.sites.add(cls.site1)
        cls.EDIT_POST_URL = reverse('post_edit', args=[USER, cls.post.id])
        cls.VIEW_POST_URL = reverse('post', args=[USER, cls.post.id])
        cls.COMMENT_URL = reverse('add_comment', args=[USER, cls.post.id])

    def test_authorized_urls_exists_at_desired_location(self):
        """Страницы доступны авторизованному пользователю."""
        urls = (
            NEW_POST_URL,
            self.EDIT_POST_URL
        )
        for url in urls:
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertEqual(response.status_code, 200)

    def test_guest_urls_exists_at_desired_location(self):
        """Страницы доступны любому пользователю."""
        urls = (
            INDEX_URL,
            GROUP_POST_URL,
            USER_URL,
            self.VIEW_POST_URL,
            AUTHOR_URL,
            SPEC_URL,
            )
        for url in urls:
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, 200)

    def test_authorized_urls_inaccessible_for_wrong_user(self):
        """Редактирование и комментирование
        недоступно пользователю, отличному от автора поста"""
        urls = (
            self.EDIT_POST_URL,
            self.COMMENT_URL
        )
        for url in urls:
            with self.subTest(url=url):
                response = self.authorized_client2.get(url)
                self.assertEqual(response.status_code, 302)

    def test_authorized_urls_inaccessible_for_unathorized_user(self):
        """Редактирование и комментирование
        недоступно неавторизованному пользователю."""
        urls = (
            self.EDIT_POST_URL,
            self.COMMENT_URL
        )
        for url in urls:
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, 302)

    def test_wrong_url_returns_404(self):
        """Неверная страница возвращает код 404"""
        response = self.guest_client.get(WRONG_USER_URL)
        self.assertEqual(response.status_code, 404)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        cache.clear()
        templates_url_names = {
            INDEX_URL: 'index.html',
            NEW_POST_URL: 'new.html',
            GROUP_POST_URL: 'group.html',
            USER_URL: 'profile.html',
            self.VIEW_POST_URL: 'post.html',
            self.EDIT_POST_URL: 'new.html',
            AUTHOR_URL: 'flatpages/default.html',
            SPEC_URL: 'flatpages/default.html'
        }
        for url, template in templates_url_names.items():
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertTemplateUsed(response, template)
