import pytest

from django.conf import settings

from .conftest import URL
from news.forms import CommentForm

pytestmark = pytest.mark.django_db


def test_news_count(client, all_news):
    response = client.get(URL.home)
    news_count = (response.context['object_list']).count()
    assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE


def test_news_order(client):
    response = client.get(URL.home)
    object_list = response.context['object_list']
    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


def test_comments_order(client, comments, news):
    response = client.get(URL.detail)
    assert 'news' in response.context
    news = response.context['news']
    all_comments = news.comment_set.all()
    all_timestamps = [comment.created for comment in all_comments]
    sorted_timestamps = sorted(all_timestamps)
    assert all_timestamps == sorted_timestamps


def test_client_has_form(client, author_client, news):
    response = client.get(URL.detail)
    author_response = author_client.get(URL.detail)
    assert (
        isinstance(author_response.context['form'], CommentForm)
        and 'form' not in response.context
    )
