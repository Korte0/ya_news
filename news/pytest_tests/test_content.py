import pytest
from django.conf import settings

from news.forms import CommentForm

pytestmark = pytest.mark.django_db


def test_news_count(client, all_news, url_home):
    response = client.get(url_home)
    news_count = (response.context['object_list']).count()
    assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE


def test_news_order(client, url_home):
    response = client.get(url_home)
    object_list = response.context['object_list']
    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


def test_comments_order(client, comments, news, url_detail):
    response = client.get(url_detail)
    assert 'news' in response.context
    news = response.context['news']
    all_comments = news.comment_set.all()
    all_timestamps = [comment.created for comment in all_comments]
    sorted_timestamps = sorted(all_timestamps)
    assert all_timestamps == sorted_timestamps


def test_anonymous_client_has_no_form(client, news, url_detail):
    response = client.get(url_detail)
    assert 'form' not in response.context


def test_authorized_client_has_form(author_client, news, url_detail):
    response = author_client.get(url_detail)
    assert 'form' in response.context
    assert isinstance(response.context['form'], CommentForm)
