from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note

UserModel = get_user_model()


class TestRoutes(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.author = UserModel.objects.create(username='author')
        cls.user = UserModel.objects.create(username='user')
        cls.note = Note.objects.create(
            title='Title',
            text='Sample text',
            slug='note-slug',
            author=cls.author,
        )

    def test_pages_availability(self):
        urls = [
            'notes:home',
            'users:login',
            'users:logout',
            'users:signup',
        ]
        urls_user = (
            'notes:list',
            'notes:add',
            'notes:success',
        )
        urls.extend(urls_user)
        for name in urls:
            if name in urls_user:
                self.client.force_login(self.user)
                urls_user = ()
            with self.subTest(name):
                url = reverse(name)
                res = self.client.get(url)
                self.assertEqual(res.status_code, HTTPStatus.OK)

    def test_note_edit_delete(self):
        statuses = (
            (self.author, HTTPStatus.OK),
            (self.user, HTTPStatus.NOT_FOUND),
        )
        urls = ('notes:detail', 'notes:edit', 'notes:delete')
        for user, status in statuses:
            self.client.force_login(user)
            for name in urls:
                url = reverse(name, kwargs={'slug': self.note.slug})
                res = self.client.get(url)
                self.assertEqual(res.status_code, status)

    def test_redirects(self):
        urls = (
            ('notes:detail', {'slug': self.note.slug}),
            ('notes:edit', {'slug': self.note.slug}),
            ('notes:delete', {'slug': self.note.slug}),
            ('notes:add', None),
            ('notes:success', None),
            ('notes:list', None),
        )
        login_url = reverse('users:login')
        for name, slug in urls:
            with self.subTest(name):
                url = reverse(name, kwargs=slug if slug else None)
                expected_url = f'{login_url}?next={url}'
                res = self.client.get(url)
                self.assertRedirects(res, expected_url)
