from django.test import TestCase
from django.contrib.auth.models import User
from .models import Mood, JournalEntry
from django.urls import reverse
from datetime import date


class MoodJournalTestCase(TestCase):
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword'
        )
        
        # Create test mood and journal entry
        self.mood = Mood.objects.create(
            user=self.user,
            mood_type='happy',
            date=date.today()
        )
        
        self.entry = JournalEntry.objects.create(
            user=self.user,
            title='Test Entry',
            content='This is a test journal entry.',
            date=date.today()
        )
    
    def test_mood_model(self):
        self.assertEqual(self.mood.user, self.user)
        self.assertEqual(self.mood.mood_type, 'happy')
        self.assertEqual(self.mood.date, date.today())
    
    def test_journal_entry_model(self):
        self.assertEqual(self.entry.user, self.user)
        self.assertEqual(self.entry.title, 'Test Entry')
        self.assertEqual(self.entry.content, 'This is a test journal entry.')
        self.assertEqual(self.entry.date, date.today())
    
    def test_login_required(self):
        # Test that login is required to access protected views
        response = self.client.get(reverse('home'))
        self.assertRedirects(response, f'/accounts/login/?next={reverse("home")}')
    
    def test_authenticated_access(self):
        # Test that authenticated users can access protected views
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
