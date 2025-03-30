from datetime import datetime, timedelta
from collections import namedtuple

import pytest
from django.conf import settings
from django.test.client import Client
from django.urls import reverse
from django.utils import timezone

from news.models import Comment, News


@pytest.fixture
def news():
    news = News.objects.create(
        title='Заголовок',
        text='Текст новости',
    )
    return news


@pytest.fixture()
def url_home():
    return reverse('news:home')


@pytest.fixture()
def url_login():
    return reverse('users:login')


@pytest.fixture()
def url_logout():
    return reverse('users:logout')


@pytest.fixture()
def url_signup():
    return reverse('users:signup')


@pytest.fixture()
def url_detail(news):
    return reverse('news:detail', args=(news.id,))


@pytest.fixture()
def url_edit(news):
    return reverse('news:edit', args=(news.id,))


@pytest.fixture()
def url_delete(news):
    return reverse('news:delete', args=(news.id,))


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def not_author(django_user_model):
    return django_user_model.objects.create(username='Не автор')


@pytest.fixture
def author_client(author):
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def not_author_client(not_author):
    client = Client()
    client.force_login(not_author)
    return client


@pytest.fixture
def comment(author, news):
    comment = Comment.objects.create(
        news=news,
        author=author,
        text='Текст комментария',
    )
    return comment


@pytest.fixture
def all_news():
    today = datetime.today()
    for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1):
        News.objects.create(
            title=f'Новость {index}',
            text='Просто текст.',
            date=today - timedelta(days=index),
        )


@pytest.fixture
def comments(author, news):
    now = timezone.now()
    for index in range(2):
        comment = Comment.objects.create(
            news=news,
            author=author,
            text=f'Текст {index}',
        )
        comment.created = now + timedelta(days=index)
        comment.save()
