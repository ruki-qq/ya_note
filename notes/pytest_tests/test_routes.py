from http import HTTPStatus

import pytest
from django.urls import reverse
from pytest_django.asserts import assertRedirects


@pytest.mark.parametrize(
    'name', ('notes:home', 'users:login', 'users:logout', 'users:signup')
)
def test_pages_availability_anon(client, name):
    url = reverse(name)
    res = client.get(url)
    assert res.status_code == HTTPStatus.OK


@pytest.mark.parametrize('name', ('notes:list', 'notes:add', 'notes:success'))
def test_pages_availability_user(admin_client, name):
    url = reverse(name)
    res = admin_client.get(url)
    assert res.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'param_client, status',
    (
        (pytest.lazy_fixture('admin_client'), HTTPStatus.NOT_FOUND),
        (pytest.lazy_fixture('author_client'), HTTPStatus.OK),
    ),
)
@pytest.mark.parametrize(
    'name', ('notes:detail', 'notes:edit', 'notes:delete')
)
def test_note_pages_availability(param_client, status, name, note_slug_kwargs):
    url = reverse(name, kwargs=note_slug_kwargs)
    res = param_client.get(url)
    assert res.status_code == status


@pytest.mark.parametrize(
    'name, kwargs',
    (
        ('notes:detail', pytest.lazy_fixture('note_slug_kwargs')),
        ('notes:edit', pytest.lazy_fixture('note_slug_kwargs')),
        ('notes:delete', pytest.lazy_fixture('note_slug_kwargs')),
        ('notes:add', None),
        ('notes:success', None),
        ('notes:list', None),
    ),
)
def test_redirects(client, name, kwargs):
    login_url = reverse('users:login')
    url = reverse(name, kwargs=kwargs) if kwargs else reverse(name)
    expected_url = f'{login_url}?next={url}'
    res = client.get(url)
    assertRedirects(res, expected_url)
