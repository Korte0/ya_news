from http import HTTPStatus

import pytest
from pytest_django.asserts import assertFormError, assertRedirects

from news.forms import BAD_WORDS, WARNING
from news.models import Comment

pytestmark = pytest.mark.django_db

FORM_DATA = {'text': 'Новый текст'}


def test_user_can_create_comment(author_client, author, news, url_detail):
    Comment.objects.filter().delete()
    response = author_client.post(url_detail, data=FORM_DATA)
    assertRedirects(response, f'{url_detail}#comments')
    assert Comment.objects.count() == 1
    new_comment = Comment.objects.get()
    assert new_comment.text == FORM_DATA['text']
    assert new_comment.author == author
    assert new_comment.news == news


def test_anonymous_user_cant_create_comment(client, news, url_detail, url_login):
    expected_count = Comment.objects.count()
    response = client.post(url_detail, data=FORM_DATA)
    expected_url = f'{url_login}?next={url_detail}'
    comments_count = Comment.objects.count()
    assertRedirects(response, expected_url)
    assert expected_count == comments_count


def test_user_cant_use_bad_words(author_client, news, url_detail):
    expected_count = Comment.objects.count()
    bad_words_data = {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}
    response = author_client.post(url_detail, data=bad_words_data)
    comments_count = Comment.objects.count()
    assert comments_count == expected_count
    assertFormError(
        response,
        form='form',
        field='text',
        errors=WARNING
    )


def test_author_can_edit_comment(
        author_client,
        author,
        comment,
        news,
        url_detail,
        url_edit,
):
    response = author_client.post(url_detail, FORM_DATA)
    url_to_comments = f'{url_detail}#comments'
    response = author_client.post(url_edit, data=FORM_DATA)
    assertRedirects(response, url_to_comments)
    new_comment = Comment.objects.get(id=comment.id)
    assert new_comment.text == FORM_DATA['text']
    assert new_comment.author == author
    assert new_comment.news == news


def test_user_cant_edit_comment_of_another_user(
        not_author_client,
        comment,
        url_edit,
):
    response = not_author_client.post(url_edit, FORM_DATA)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment_from_db = Comment.objects.get(id=comment.id)
    assert comment.text == comment_from_db.text
    assert comment.author == comment_from_db.author
    assert comment.news == comment_from_db.news


def test_author_can_delete_comment(
        author_client,
        news, comment,
        url_detail,
        url_delete
):
    expected_count = Comment.objects.count() - 1
    url_to_comments = f'{url_detail}#comments'
    response = author_client.post(url_delete)
    assertRedirects(response, url_to_comments)
    comments_count = Comment.objects.count()
    assert comments_count == expected_count


def test_user_cant_delete_comment_of_another_user(
        not_author_client,
        comment,
        url_delete,
):
    expected_count = Comment.objects.count()
    response = not_author_client.post(url_delete)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == expected_count
