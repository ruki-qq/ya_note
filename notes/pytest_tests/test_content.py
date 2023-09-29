import pytest

from django.urls import reverse


@pytest.mark.parametrize(
    'param_client, note_in_list',
    (
        (pytest.lazy_fixture('admin_client'), False),
        (pytest.lazy_fixture('author_client'), True),
    ),
)
def test_notes_list(param_client, note_in_list, note):
    url = reverse('notes:list')
    res = param_client.get(url)
    assert (note in res.context['object_list']) is note_in_list


@pytest.mark.parametrize(
    'name, kwargs',
    (
        ('notes:add', None),
        ('notes:edit', pytest.lazy_fixture('note_slug_kwargs')),
    ),
)
def test_pages_contains_form(author_client, name, kwargs):
    url = reverse(name, kwargs=kwargs)
    res = author_client.get(url)
    assert 'form' in res.context
