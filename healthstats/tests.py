from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from healthstats.models import HealthEvent, EventType
from datetime import datetime


class HealthEventTest(TestCase):

    def setUp(self):

        # self.client = Client()

        self.user = get_user_model().objects.create_user(
            username='testuser',
            email='test@email.com',
            password='secret'
        )

        self.temp_event_type = EventType.objects.create(
            name="Temperature",
            description="a measurement of body temperature"
        )

        self.event = HealthEvent.objects.create(
            author=self.user,
            event_type=self.temp_event_type,
            when=datetime.datetime.now(),
            value=100.00,
            notes="a thought about this temp!"
        )

    # def test_string_representation(self):
    #     event = EventType(title='A sample title')
    #     self.assertEqual(str(post), post.title)

    # def test_post_content(self):
    #     self.assertEqual(f'{self.post.title}', 'test title')
    #     self.assertEqual(f'{self.post.author}', 'testuser')
    #     self.assertEqual(f'{self.post.body}',
    #                      'test body content that is longer')

    def test_post_list_view(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.event.value)
        self.assertTemplateUsed(response, 'home.html')

    # def test_post_detail_view(self):
    #     # not sure why self.post from setUp() is put in the second index but w/e.
    #     # print(f'the value of "id" self.post in this test case is: {self.post.id}')
    #     # so im just asking if its there at the ID.
    #     response = self.client.get(f'/blog/post/{self.post.id}/')
    #     no_response = self.client.get('/blog/post/100000/')
    #     self.assertEqual(response.status_code, 200)
    #     self.assertEqual(no_response.status_code, 404)
    #     self.assertContains(response, 'test title')
    #     self.assertTemplateUsed(response, 'post_detail.html')

    # def test_post_create_view_when_logged_in(self):  # new
    #     self.client.login(username='testuser', password='secret')
    #     response = self.client.post(reverse('post_new'), {
    #         'title': 'New title',
    #         'body': 'New text',
    #         'author': self.user.id,
    #     })
    #     self.assertEqual(response.status_code, 302)
    #     self.assertEqual(Post.objects.last().title, 'New title')
    #     self.assertEqual(Post.objects.last().body, 'New text')

    # def test_post_create_view_when_logged_out(self):  # new
    #     response = self.client.post(reverse('post_new'), {
    #         'title': 'New title',
    #         'body': 'New text',
    #         'author': self.user.id,
    #     })
    #     self.assertEqual(response.status_code, 403)

    # def test_post_update_view_when_logged_in(self):
    #     self.client.login(username='testuser', password='secret')
    #     response = self.client.post(reverse('post_update', args=f'{self.post.id}'), {
    #         'title': 'Updated title',
    #         'body': 'Updated text',
    #     })

    #     self.assertEqual(response.status_code, 200)

    # def test_post_update_view_when_logged_out(self):

    #     response = self.client.post(
    #         reverse('post_update', args=[f'{self.post.id}']),
    #         {'title': 'Updated title', 'body': 'Updated text', }
    #     )

    #     self.assertEqual(response.status_code, 403)

    # def test_if_user_can_delete_a_new_post_without_login(self):
    #     response = self.client.post(
    #         reverse('post_delete', args=f'{self.post.id}'))
    #     self.assertEqual(response.status_code, 403)

    # def test_if_user_can_delete_post_when_logged_in(self):
    #     self.client.login(username='testuser', password='secret')
    #     response = self.client.get(f'/blog/post/{self.post.id}/delete')
    #     self.assertEqual(response.status_code, 200)
