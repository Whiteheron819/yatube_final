from django.db import models
from django.contrib.auth import get_user_model


User = get_user_model()


class Group(models.Model):
    title = models.CharField('Заголовок', max_length=200,
                             help_text='Название группы')
    description = models.TextField()
    slug = models.SlugField(null=False, unique=True, max_length=80)

    def __str__(self):
        return self.title

    class Meta(object):
        verbose_name = 'Группа'
        verbose_name_plural = 'Группы'


class Post(models.Model):
    text = models.TextField('Текст', help_text='Поле для сообщения')
    pub_date = models.DateTimeField("date published", auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name="posts")
    group = models.ForeignKey(Group, on_delete=models.SET_NULL,
                              blank=True, null=True,
                              related_name="posts", verbose_name='Группа',
                              help_text='Выбор сообщества')
    image = models.ImageField(upload_to='posts/', blank=True, null=True)

    def __str__(self):
        return f'{self.text[:15]} {self.author} {self.pub_date} {self.group}'

    class Meta(object):
        ordering = ("-pub_date",)
        verbose_name = 'Сообщение'
        verbose_name_plural = 'Сообщения'


class Comment(models.Model):
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE, related_name="comments"
        )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="comments",
        )
    text = models.TextField('Текст', help_text='Поле для комментария')
    created = models.DateTimeField("date published", auto_now_add=True)

    class Meta(object):
        ordering = ("-post",)
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'


class Follow(models.Model):
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="following", null=True
        )
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="follower", null=True
        )
