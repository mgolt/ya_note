from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note


User = get_user_model()


class TestNoteCreation(TestCase):

    TITLE = 'Заголовок'
    TEXT = 'Описание'
    SLUG = 'note_slug'

    @classmethod
    def setUpTestData(cls):

        cls.url = reverse('notes:add', )
        cls.form_data = {
            'title': cls.TITLE,
            'text': cls.TEXT,
            'slug': cls.SLUG,
        }

    def test_anonymous_user_cant_create_note(self):
        self.client.post(self.url, data=self.form_data)
        # Считаем количество заметок.
        notes_count = Note.objects.count()
        # Ожидаем, что заметок в базе нет - сравниваем с нулём.
        self.assertEqual(notes_count, 0)


class TestNoteBrowseEditDelete(TestCase):

    NOTE_TEXT = 'Text'
    NEW_NOTE_TEXT = 'New text'

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='UserAuthor')
        cls.reader = User.objects.create(username='UserReader')
        cls.auth_client_author = Client()
        cls.auth_client_author.force_login(cls.author)
        cls.auth_client_reader = Client()
        cls.auth_client_reader.force_login(cls.reader)
        cls.note = Note.objects.create(
            title='Title',
            text='Text',
            slug='Slug',
            author=cls.author,
        )
        cls.url_details = reverse('notes:detail', args=(cls.note.slug,))
        cls.url_edit = reverse('notes:edit', args=(cls.note.slug,))
        cls.url_delete = reverse('notes:delete', args=(cls.note.slug,))
        cls.url_done = reverse('notes:success')
        cls.form_data = {
            'title': 'New title',
            'text': cls.NEW_NOTE_TEXT,
            'slug': 'new_slug'
        }

    def test_user_cant_browse_note_of_another_user(self):
        response = self.auth_client_reader.get(self.url_details)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_user_cant_edit_note_of_another_user(self):
        response = self.auth_client_reader.post(self.url_edit, self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.note.refresh_from_db()
        self.assertEqual(self.note.text, self.NOTE_TEXT)

    def test_user_cant_delete_note_of_another_user(self):
        response = self.auth_client_reader.delete(self.url_delete)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        count_notes = Note.objects.count()
        self.assertEqual(count_notes, 1)

    def test_author_can_edit_note(self):
        response = self.auth_client_author.post(self.url_edit, self.form_data)
        self.assertRedirects(response, self.url_done)
        self.note.refresh_from_db()
        self.assertEqual(self.note.text, self.NEW_NOTE_TEXT)

    def test_author_can_delete_note(self):
        response = self.auth_client_author.delete(self.url_delete)
        self.assertRedirects(response, self.url_done)
        count_notes = Note.objects.count()
        self.assertEqual(count_notes, 0)
