from http import HTTPStatus

import pytest
from pytest_django.asserts import assertRedirects

from .conftest import URL

pytestmark = pytest.mark.django_db

NOT_AUTHOR_CLIENT = pytest.lazy_fixture('not_author_client')
AUTHOR_CLIENT = pytest.lazy_fixture('author_client')

def test_home_availability_for_anonymous_user(client):
    response = client.get(URL.home)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'url, parametrized_client, expected_status',
    (
        (URL.home, NOT_AUTHOR_CLIENT, HTTPStatus.OK),
        (URL.detail, NOT_AUTHOR_CLIENT, HTTPStatus.OK),
        (URL.login, NOT_AUTHOR_CLIENT, HTTPStatus.OK),
        (URL.logout, NOT_AUTHOR_CLIENT, HTTPStatus.OK),
        (URL.signup, NOT_AUTHOR_CLIENT, HTTPStatus.OK),
        (URL.edit, AUTHOR_CLIENT, HTTPStatus.OK),
        (URL.delete, AUTHOR_CLIENT, HTTPStatus.OK),
        (URL.edit, NOT_AUTHOR_CLIENT, HTTPStatus.NOT_FOUND),
        (URL.delete, NOT_AUTHOR_CLIENT, HTTPStatus.NOT_FOUND),
    ),
)
def test_pages_availability_for_anonymous_user(
    url,
    parametrized_client,
    expected_status,
    comment
):
    response = parametrized_client.get(url)
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    'url',
    (URL.edit, URL.delete),
)
def test_redirects(client, url, comment):
    expected_url = f'{URL.login}?next={url}'
    response = client.get(url)
    assertRedirects(response, expected_url)
