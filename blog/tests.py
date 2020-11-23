from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from blog.models import Post



class BlogTest(TestCase):

    def setUp(self):

        # self.client = Client()

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
        # not sure why self.post from setUp() is put in the second index but w/e. 
        # print(f'the value of "id" self.post in this test case is: {self.post.id}')
        #so im just asking if its there at the ID. 
        response = self.client.get(f'/blog/post/{self.post.id}/')
        no_response = self.client.get('/blog/post/100000/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(no_response.status_code, 404)
        self.assertContains(response, 'test title')
        self.assertTemplateUsed(response, 'post_detail.html')

    def test_if_user_can_edit_a_post_without_login(self):
        response = self.client.get(f'/blog/post/{self.post.id}/update')
        self.assertEqual(response.status_code, 403)

    def test_if_user_can_create_a_new_post_without_login(self):
        response = self.client.get('/blog/post/new/')
        self.assertEqual(response.status_code, 403)

    def test_if_user_can_edit_post_when_logged_in(self):
        self.client.login(username='testuser', password='secret')
        response = self.client.get(f'/blog/post/{self.post.id}/update')
        self.assertEqual(response.status_code, 200)

    def test_if_user_can_access_create_new_post_when_logged_in(self):
        self.client.login(username='testuser', password='secret')
        response = self.client.get('/blog/post/new/')
        self.assertEqual(response.status_code, 200)