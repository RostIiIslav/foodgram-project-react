from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models



class User(AbstractUser):
    email = models.EmailField(verbose_name="Email", unique=True)
    username = models.CharField('Никнейм', unique=True, max_length=20)
    last_name = models.CharField('Фамилия', max_length=120)
    first_name = models.CharField('Имя', max_length=120)

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username[:50]


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
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='subscription_unique'
            )
        ]

    def clean(self):
        if self.author == self.user:
            raise ValidationError('Нельзя подписаться на себя')
        if Subscription.objects.filter(
                author=self.author, user=self.user).exists():
            raise ValidationError('Вы уже подписаны')

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)
