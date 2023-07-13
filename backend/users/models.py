from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    email = models.EmailField(verbose_name="Email", unique=True)

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username


class Subscription(models.Model):
    user = models.ForeignKey(User, verbose_name='Подписчик',
                             on_delete=models.CASCADE,
                             related_name='subscriptions')
    author = models.ForeignKey(User, verbose_name='Автор',
                               on_delete=models.CASCADE,
                               related_name='author_subscriptions')

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
