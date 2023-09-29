from http import HTTPStatus

import pytest
from pytest_django.asserts import assertFormError, assertRedirects
from pytils.translit import slugify

from django.urls import reverse

from notes.forms import WARNING
from notes.models import Note


def test_create_note_auth_user(author_client, author, form_data):
    url = reverse('notes:add')
    res = author_client.post(url, data=form_data)
    assertRedirects(res, reverse('notes:success'))
    assert Note.objects.count() == 1
    new_note = Note.objects.get()
    assert new_note.title == form_data['title']
    assert new_note.text == form_data['text']
    assert new_note.slug == form_data['slug']
    assert new_note.author == author


@pytest.mark.django_db
def test_create_note_anon_user(client, form_data):
    url = reverse('notes:add')
    res = client.post(url, data=form_data)
    login_url = reverse('users:login')
    expected_url = f'{login_url}?next={url}'
    assertRedirects(res, expected_url)
    assert Note.objects.count() == 0


def test_not_uniq_slug(author_client, note, form_data):
    url = reverse('notes:add')
    form_data['slug'] = note.slug
    res = author_client.post(url, data=form_data)
    assertFormError(res, 'form', 'slug', errors=(note.slug + WARNING))
    assert Note.objects.count() == 1


def test_empty_slug(author_client, form_data):
    url = reverse('notes:add')
    form_data.pop('slug')
    res = author_client.post(url, data=form_data)
    assertRedirects(res, reverse('notes:success'))
    assert Note.objects.count() == 1
    new_note = Note.objects.get()
    expected_slug = slugify(form_data['title'])
    assert new_note.slug == expected_slug


def test_edit_note_author(author_client, form_data, note, note_slug_kwargs):
    url = reverse('notes:edit', kwargs=note_slug_kwargs)
    response = author_client.post(url, form_data)
    assertRedirects(response, reverse('notes:success'))
    note.refresh_from_db()
    assert note.title == form_data['title']
    assert note.text == form_data['text']
    assert note.slug == form_data['slug']


def test_edit_note_user(admin_client, form_data, note, note_slug_kwargs):
    url = reverse('notes:edit', kwargs=note_slug_kwargs)
    res = admin_client.post(url, form_data)
    assert res.status_code == HTTPStatus.NOT_FOUND
    note_from_db = Note.objects.get(pk=note.pk)
    assert note.title == note_from_db.title
    assert note.text == note_from_db.text
    assert note.slug == note_from_db.slug


# test_logic.py
...


def test_author_can_delete_note(author_client, note_slug_kwargs):
    url = reverse('notes:delete', kwargs=note_slug_kwargs)
    res = author_client.post(url)
    assertRedirects(res, reverse('notes:success'))
    assert Note.objects.count() == 0


def test_other_user_cant_delete_note(
    admin_client, form_data, note_slug_kwargs
):
    url = reverse('notes:delete', kwargs=note_slug_kwargs)
    res = admin_client.post(url)
    assert res.status_code == HTTPStatus.NOT_FOUND
    assert Note.objects.count() == 1
