from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse


class HomePageTest(TestCase):
  
    def setUp(self):
        self.client = Client()
        
        self.user = get_user_model().objects.create_user(
            username='testuser',
            email='test@email.com',
            password='secret'
        )

    def test_view_url_exists_at_proper_location(self):
        response = self.client.get('/', follow=True)
        self.assertEqual(response.status_code, 200)

    def test_view_by_url_name(self):
        response = self.client.get(reverse('home'), follow=True)
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('home'), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home.html')

    def test_private_view_is_private(self):
        response = self.client.get('/health/', follow=True)
        self.assertEqual(response.status_code, 403)

    