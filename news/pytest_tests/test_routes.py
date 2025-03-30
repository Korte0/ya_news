from http import HTTPStatus

import pytest
from pytest_django.asserts import assertRedirects


pytestmark = pytest.mark.django_db

NOT_AUTHOR_CLIENT = pytest.lazy_fixture('not_author_client')
AUTHOR_CLIENT = pytest.lazy_fixture('author_client')


def test_home_availability_for_anonymous_user(client, url_home):
    response = client.get(url_home)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'url, parametrized_client, expected_status',
    (
        ('url_home', NOT_AUTHOR_CLIENT, HTTPStatus.OK),
        ('url_detail', NOT_AUTHOR_CLIENT, HTTPStatus.OK),
        ('url_login', NOT_AUTHOR_CLIENT, HTTPStatus.OK),
        ('url_logout', NOT_AUTHOR_CLIENT, HTTPStatus.OK),
        ('url_signup', NOT_AUTHOR_CLIENT, HTTPStatus.OK),
        ('url_edit', AUTHOR_CLIENT, HTTPStatus.OK),
        ('url_delete', AUTHOR_CLIENT, HTTPStatus.OK),
        ('url_edit', NOT_AUTHOR_CLIENT, HTTPStatus.NOT_FOUND),
        ('url_delete', NOT_AUTHOR_CLIENT, HTTPStatus.NOT_FOUND),
    ),
)
def test_pages_availability_for_anonymous_user(
    url,
    parametrized_client,
    expected_status,
    comment,
    request,
):
    url = request.getfixturevalue(url)
    response = parametrized_client.get(url)
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    'url',
    ('url_edit', 'url_delete'),
)
def test_redirects(client, url, comment, request, url_login):
    url = request.getfixturevalue(url)
    expected_url = f'{url_login}?next={url}'
    response = client.get(url)
    assertRedirects(response, expected_url)
