'''
    User Application Tests
    user/tests.py
    @author Teerapat Kraisrisirikul (810Teams)
    @status discontinued
'''

from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase


BOB = {'username': 'bob', 'password': 'password303'}
ALICE = {'username': 'alice', 'password': 'password41153'}


class LoginTest(APITestCase):
    ''' Login test '''
    def setUp(self):
        ''' Set up '''
        get_user_model().objects.create_user(username=BOB['username'], password=BOB['password'])
        get_user_model().objects.create_user(username=ALICE['username'], password=ALICE['password'])

    def test_login_valid(self):
        ''' Test valid login credentials '''
        response = self.client.post('/api/user/login/', {
            'username': BOB['username'],
            'password': BOB['password']
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_login_invalid(self):
        ''' Test invalid login credentials '''
        response = self.client.post('/api/user/login/', {
            'username': BOB['username'],
            'password': BOB['password'] + '.'
        })

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class UserTest(APITestCase):
    ''' User test '''
    def setUp(self):
        ''' Set up '''
        self.parameters = ('id', 'username', 'name', 'email', 'nickname', 'bio', 'profile_picture', 'cover_photo',
                           'birthdate', 'created_at', 'updated_at')

    def test_retrieve_user_not_logged_in(self):
        ''' Test retrieve user data when not logged in '''
        response =  self.client.get(
            '/api/user/user/{}/'.format(get_user_model().objects.get(username=BOB['username']).id)
        )

        for i in (1, 2, 4, 6):
            self.assertIn(self.parameters[i], response.data)

        for i in (0, 3, 5, 7, 8, 9, 10):
            self.assertNotIn(self.parameters[i], response.data)

    def test_retrieve_user_logged_in(self):
        ''' Test retrieve user data when logged in '''
        self.client.login(username=BOB['username'], password=BOB['password'])

        response = self.client.get(
            '/api/user/user/{}/'.format(get_user_model().objects.get(username=BOB['username']).id)
        )

        for i in self.parameters:
            self.assertIn(i, response.data)

        response = self.client.get(
            '/api/user/user/{}/'.format(get_user_model().objects.get(username=ALICE['username']).id)
        )

        for i in self.parameters:
            self.assertIn(i, response.data)

        self.client.logout()
