from rest_framework import status
from rest_framework.test import APITestCase

from user.models import User

BOB = {'username': 'bob', 'password': 'password303'}
ALICE = {'username': 'alice', 'password': 'password41153'}


class LoginTest(APITestCase):
    def setUp(self):
        User.objects.create_user(username=BOB['username'], password=BOB['password'])
        User.objects.create_user(username=ALICE['username'], password=ALICE['password'])

    def test_login_valid(self):
        response = self.client.post('/api/user/login/', {
            'username': BOB['username'],
            'password': BOB['password']
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_login_invalid(self):
        response = self.client.post('/api/user/login/', {
            'username': BOB['username'],
            'password': BOB['password'] + '.'
        })

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class UserTest(APITestCase):
    def setUp(self):
        self.parameters = ('id', 'username', 'name', 'email', 'nickname', 'bio', 'profile_picture', 'cover_photo',
                           'birthdate', 'created_at', 'updated_at')

    def test_retrieve_user_not_logged_in(self):
        response =  self.client.get('/api/user/user/{}/'.format(User.objects.get(username=BOB['username']).id))

        for i in (1, 2, 4, 6):
            self.assertIn(self.parameters[i], response.data)

        for i in (0, 3, 5, 7, 8, 9, 10):
            self.assertNotIn(self.parameters[i], response.data)

    def test_retrieve_user_logged_in(self):
        self.client.login(username=BOB['username'], password=BOB['password'])

        response = self.client.get('/api/user/user/{}/'.format(User.objects.get(username=BOB['username']).id))

        for i in self.parameters:
            self.assertIn(i, response.data)

        response = self.client.get('/api/user/user/{}/'.format(User.objects.get(username=ALICE['username']).id))

        for i in self.parameters:
            self.assertIn(i, response.data)

        self.client.logout()
