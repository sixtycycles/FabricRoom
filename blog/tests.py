from django.test import TestCase
from django.urls import reverse
from blog.models import Post


class PostModelTest(TestCase):
    def setUp(self):
        Post.objects.create(body='just a test')

    def test_text_content(self):
        post = Post.objects.get(id=1)
        expected_object_name = f'{post.body}'
        self.assertEqual(expected_object_name, 'just a test')


class HomePageTest(TestCase):
    def setUp(self):
        Post.objects.create(title = 'test title', body = 'test body content that is longer')

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