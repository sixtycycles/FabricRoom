from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from blog.models import Post



class HomePageTest(TestCase):

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

class BlogTest(TestCase):
    def setUp(self):

        self.user = get_user_model().objects.create_user(
            username='testuser',
            email='test@email.com',
            password='secret'
        )

        self.post = Post.objects.create(
            author=self.user,
            title='test title',
            body='test body content that is longer',
            published=True
        )

    def test_string_representation(self):
        post = Post(title='A sample title')
        self.assertEqual(str(post), post.title)

    def test_post_content(self):
        self.assertEqual(f'{self.post.title}', 'test title')
        self.assertEqual(f'{self.post.author}', 'testuser')
        self.assertEqual(f'{self.post.body}',
                         'test body content that is longer')

    def test_post_list_view(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'test title')
        self.assertTemplateUsed(response, 'home.html')

    def test_post_detail_view(self):
        response = self.client.get('/blog/post/1/')
        no_response = self.client.get('/blog/post/100000/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(no_response.status_code, 404)
        self.assertContains(response, 'test title')
        self.assertTemplateUsed(response, 'post_detail.html')
