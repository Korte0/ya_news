from http import HTTPStatus

import pytest
from pytest_django.asserts import assertFormError, assertRedirects

from .conftest import URL
from news.forms import BAD_WORDS, WARNING
from news.models import Comment

pytestmark = pytest.mark.django_db

FORM_DATA = {'text': 'Новый текст'}


def test_user_can_create_comment(author_client, author, news):
    response = author_client.post(URL.detail, data=FORM_DATA)
    assertRedirects(response, f'{URL.detail}#comments')
    assert Comment.objects.count() == 1
    new_comment = Comment.objects.get()
    Comment.objects.filter().delete()
    assert all(
        (
            new_comment.text == FORM_DATA['text'],
            new_comment.author == author,
            new_comment.news == news,
        )
    )


def test_anonymous_user_cant_create_comment(client, news):
    expected_count = Comment.objects.count()
    response = client.post(URL.detail, data=FORM_DATA)
    expected_url = f'{URL.login}?next={URL.detail}'
    comments_count = Comment.objects.count()
    assertRedirects(response, expected_url)
    assert expected_count == comments_count


def test_user_cant_use_bad_words(author_client, news):
    expected_count = Comment.objects.count()
    bad_words_data = {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}
    response = author_client.post(URL.detail, data=bad_words_data)
    assertFormError(
        response,
        form='form',
        field='text',
        errors=WARNING
    )
    comments_count = Comment.objects.count()
    assert comments_count == expected_count


def test_author_can_edit_comment(
        author_client,
        comment,
        news,
):
    response = author_client.post(URL.detail, FORM_DATA)
    url_to_comments = f'{URL.detail}#comments'
    response = author_client.post(URL.edit, data=FORM_DATA)
    assertRedirects(response, url_to_comments)
    comment = Comment.objects.get(id=comment.id)
    assert comment.text == FORM_DATA['text']


def test_user_cant_edit_comment_of_another_user(
        not_author_client,
        comment,
):
    response = not_author_client.post(URL.edit, FORM_DATA)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment_from_db = Comment.objects.get(id=comment.id)
    assert all(
        (
            comment.text == comment_from_db.text,
            comment.author == comment_from_db.author,
            comment.news == comment_from_db.news,
        )
    )



def test_author_can_delete_comment(author_client, news, comment):
    url_to_comments = f'{URL.detail}#comments'
    response = author_client.post(URL.delete)
    assertRedirects(response, url_to_comments)
    comments_count = Comment.objects.count()
    assert comments_count == 0


def test_user_cant_delete_comment_of_another_user(
        not_author_client,
        comment,
):
    response = not_author_client.post(URL.delete)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == 1
