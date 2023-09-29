import pytest

from notes.models import Note


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='Author')


@pytest.fixture
def author_client(author, client):
    client.force_login(author)
    return client


@pytest.fixture
def note(author):
    return Note.objects.create(
        title='Title',
        text='Sample text',
        slug='note-slug',
        author=author,
    )


@pytest.fixture
def note_slug_kwargs(note):
    return {'slug': note.slug}


@pytest.fixture
def form_data():
    return {
        'title': 'New Title',
        'text': 'New text',
        'slug': 'new-slug',
    }
