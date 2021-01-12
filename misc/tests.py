'''
    Miscellaneous Application Tests
    misc/tests.py
    @author Teerapat Kraisrisirikul (810Teams)
'''

from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from misc.models import FAQ


class FAQAPITest(APITestCase):
    ''' Frequently asked question (FAQ) API test '''
    def setUp(self):
        ''' Set up '''
        self.user_01 = get_user_model().objects.create_user(username='user_01', password='12345678', name='User One')

    def test_list_faq_authenticated(self):
        ''' Test list FAQ while authenticated '''
        self.client.login(username='user_01', password='12345678')

        FAQ.objects.create(question='Why do I feel not working?', answer='It\'s simple. You\'re just lazy.')
        response = self.client.get('/api/misc/faq/')
        self.assertEqual(len(response.data), 1)

        self.client.logout()

    def test_list_faq_unauthenticated(self):
        ''' Test list FAQ while unauthenticated '''
        FAQ.objects.create(question='Why do I feel not working?', answer='It\'s simple. You\'re just lazy.')
        response = self.client.get('/api/misc/faq/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_retrieve_faq_authenticated(self):
        ''' Test retrieve FAQ while authenticated '''
        self.client.login(username='user_01', password='12345678')

        faq = FAQ.objects.create(question='Why do I feel not working?', answer='It\'s simple. You\'re just lazy.')
        response = self.client.get('/api/misc/faq/{}/'.format(faq.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.client.logout()

    def test_retrieve_faq_unauthenticated(self):
        ''' Test retrieve FAQ while unauthenticated '''
        faq = FAQ.objects.create(question='Why do I feel not working?', answer='It\'s simple. You\'re just lazy.')
        response = self.client.get('/api/misc/faq/{}/'.format(faq.id))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_faq(self):
        ''' Test create FAQ '''
        self.client.login(username='user_01', password='12345678')

        response = self.client.post('/api/misc/faq/', {
            'question': 'Why do I feel not working?',
            'answer': 'It\'s simple. You\'re just lazy.'
        })
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        self.client.logout()

    def test_update_faq(self):
        ''' Test update FAQ '''
        self.client.login(username='user_01', password='12345678')

        faq = FAQ.objects.create(question='Why do I feel not working?', answer='It\'s simple. You\'re just lazy.')
        response = self.client.put('/api/misc/faq/{}/'.format(faq.id), {
            'answer': 'There are various reasons that may be causing this.'
        })
        self.assertEqual(FAQ.objects.get(pk=faq.id).answer, 'It\'s simple. You\'re just lazy.')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        faq = FAQ.objects.create(question='Why do I feel sleepy?', answer='It\'s simple. You were up all night gaming.')
        response = self.client.patch('/api/misc/faq/{}/'.format(faq.id), {
            'answer': 'You need more caffeine.'
        })
        self.assertEqual(FAQ.objects.get(pk=faq.id).answer, 'It\'s simple. You were up all night gaming.')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        self.client.logout()

    def test_delete_faq(self):
        ''' Test delete FAQ '''
        self.client.login(username='user_01', password='12345678')

        faq = FAQ.objects.create(question='Why do I feel not working?', answer='It\'s simple. You\'re just lazy.')
        response = self.client.delete('/api/misc/faq/{}/'.format(faq.id))
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        self.client.logout()
