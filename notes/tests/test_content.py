from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from notes.models import Note
from notes.forms import NoteForm


User = get_user_model()


class TestDetailPage(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='UserAuthor')

        cls.note = Note.objects.create(
            title='Заголовок',
            text='Описание',
            slug='note_slug',
            author=cls.author,
        )

        cls.detail_url = reverse('notes:edit', args=(cls.note.slug,))

    def test_anonymous_client_has_no_form(self):
        response = self.client.get(self.detail_url)
        self.assertEqual(response.context, None)

    def test_authorized_client_has_form(self):
        self.client.force_login(self.author)
        response = self.client.get(self.detail_url)
        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['form'], NoteForm)
