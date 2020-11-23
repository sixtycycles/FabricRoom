from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from blog.models import Post



class BlogTest(TestCase):

    def setUp(self):

        self.client = Client()

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
        #print(self.user)
        #print(self.post.id)
        # not sure why this gets put in the second index but w/e. 
        response = self.client.get('/blog/post/2/')
        no_response = self.client.get('/blog/post/100000/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(no_response.status_code, 404)
        self.assertContains(response, 'test title')
        self.assertTemplateUsed(response, 'post_detail.html')
