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
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_view_by_url_name(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home.html')

    def test_private_view_is_private(self):
        response = self.client.get('/secret/')
        self.assertEqual(response.status_code,403)

    #def test_redirects_to_login_page_on_not_loggedin(self):
    #     response = self.client.get(reverse(my_view))
    #     self.assertRedirects(response, reverse('login_page'))

    # def test_redirects_to_test_page_on_loggedin(self):
    #     self.client.login(username='my_username', password='my_password')
    #     response = self.client.get(reverse(my_view))
    #     self.assertRedirects(response, reverse('test'))