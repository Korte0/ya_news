from http import HTTPStatus

import pytest
from django.urls import reverse
from pytest_django.asserts import assertFormError, assertRedirects

from news.forms import BAD_WORDS, WARNING
from news.models import Comment


def test_user_can_create_comment(author_client, author, news_id, form_data):
    url = reverse('news:detail', args=news_id)
    response = author_client.post(url, data=form_data)
    assertRedirects(response, f'{url}#comments')
    assert Comment.objects.count() == 1
    new_comment = Comment.objects.get()
    assert new_comment.text == form_data['text']
    assert new_comment.author == author

@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(client, form_data, news_id):
    url = reverse('news:detail', args=news_id)
    response = client.post(url, data=form_data)
    login_url = reverse('users:login')
    expected_url = f'{login_url}?next={url}'
    assertRedirects(response, expected_url)
    assert Comment.objects.count() == 0

@pytest.mark.django_db
def test_user_cant_use_bad_words(author_client, news_id):
    url = reverse('news:detail', args=news_id)
    bad_words_data = {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}
    response = author_client.post(url, data=bad_words_data)
    assertFormError(
        response,
        form='form',
        field='text',
        errors=WARNING
    )
    comments_count = Comment.objects.count()
    assert comments_count == 0


def test_author_can_edit_comment(
        author_client,
        form_data,
        comment,
        news_id,
        comment_id
):
    url = reverse('news:detail', args=news_id)
    response = author_client.post(url, form_data)
    url_to_comments = f'{url}#comments'
    edit_url = reverse('news:edit', args=comment_id)
    response = author_client.post(edit_url, data=form_data)
    assertRedirects(response, url_to_comments)
    comment.refresh_from_db()
    assert comment.text == form_data['text']


def test_user_cant_edit_comment_of_another_user(
        not_author_client,
        form_data,
        comment,
        comment_id
):
    url = reverse('news:edit', args=comment_id)
    response = not_author_client.post(url, form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment_from_db = Comment.objects.get(id=comment.id)
    assert comment.text == comment_from_db.text


def test_author_can_delete_comment(author_client, news_id, comment_id):
    url = reverse('news:detail', args=news_id)
    url_to_comments = f'{url}#comments'
    delete_url = reverse('news:delete', args=comment_id)
    response = author_client.post(delete_url)
    assertRedirects(response, url_to_comments)
    comments_count = Comment.objects.count()
    assert comments_count == 0


def test_user_cant_delete_comment_of_another_user(
        not_author_client,
        comment,
        comment_id,
):
    url = reverse('news:delete', args=comment_id)
    response = not_author_client.post(url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == 1
