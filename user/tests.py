'''
    User Application Tests
    user/tests.py
    @author Teerapat Kraisrisirikul (810Teams)
'''

from datetime import datetime

from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from user.models import EmailPreference, StudentCommitteeAuthority


class LoginAPITest(APITestCase):
    ''' Login API test '''
    def setUp(self):
        ''' Set up '''
        get_user_model().objects.create_user(username='user_01', password='12345678', name='User One')

    def test_login_valid(self):
        ''' Test valid login credentials '''
        response = self.client.post('/api/user/login/', {
            'username': 'user_01',
            'password': '12345678'
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_login_invalid(self):
        ''' Test invalid login credentials '''
        response = self.client.post('/api/user/login/', {
            'username': 'user_01',
            'password': '12345678x',
        })

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class UserAPITest(APITestCase):
    ''' User API test '''
    def setUp(self):
        ''' Set up '''
        self.public_parameter = ('id', 'username', 'name', 'profile_picture', 'cover_photo')
        self.protected_parameters = ('nickname', 'bio', 'birthdate', 'user_group')

        self.user_01 = get_user_model().objects.create_user(username='user_01', password='12345678')
        self.user_02 = get_user_model().objects.create_user(username='user_02', password='12345678')

    def test_list(self):
        ''' Test list '''
        self.client.login(username='user_01', password='12345678')

        response = self.client.get('/api/user/user/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.client.logout()

    def test_retrieve_unauthenticated(self):
        ''' Test retrieve user data when not logged in '''
        response =  self.client.get('/api/user/user/{}/'.format(self.user_01.id))

        for i in self.public_parameter:
            self.assertIn(i, response.data)

        for i in self.protected_parameters:
            self.assertNotIn(i, response.data)

    def test_retrieve_authenticated(self):
        ''' Test retrieve user data when logged in '''
        self.client.login(username='user_01', password='12345678')

        response = self.client.get('/api/user/user/{}/'.format(self.user_01.id))

        for i in self.public_parameter + self.protected_parameters:
            self.assertIn(i, response.data)

        self.client.logout()

    def test_create(self):
        ''' Test create '''
        self.client.login(username='user_01', password='12345678')

        response = self.client.post('/api/user/user/', {
            'username': 'user_xx',
            'password': '12345678'
        })
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        self.client.logout()

    def test_update_own(self):
        ''' Test update own '''
        self.client.login(username='user_01', password='12345678')

        self.client.patch('/api/user/user/{}/'.format(self.user_01.id), {
            'nickname': 'Bob'
        })
        response = self.client.get('/api/user/user/{}/'.format(self.user_01.id))
        self.assertEqual(response.data['nickname'], 'Bob')

        self.client.logout()

    def test_update_other(self):
        ''' Test update other '''
        self.client.login(username='user_01', password='12345678')

        response = self.client.patch('/api/user/user/{}/'.format(self.user_02.id), {
            'nickname': 'Alice'
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.client.logout()

    def test_delete(self):
        ''' Test delete '''
        self.client.login(username='user_01', password='12345678')

        response = self.client.delete('/api/user/user/{}/'.format(self.user_02.id))
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        self.client.logout()


class MyUserAPITest(APITestCase):
    ''' User API test '''
    def setUp(self):
        ''' Set up '''
        get_user_model().objects.create_user(username='user_01', password='12345678')
        get_user_model().objects.create_user(username='user_02', password='12345678')

    def test_retrieve_unauthenticated(self):
        ''' Test retrieve authenticated '''
        response = self.client.get('/api/user/user/me/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_retrieve_authenticated(self):
        ''' Test retrieve authenticated '''
        self.client.login(username='user_01', password='12345678')

        response = self.client.get('/api/user/user/me/')
        self.assertEqual(response.data['id'], get_user_model().objects.get(username='user_01').id)

        self.client.logout()


class EmailPreferenceAPITest(APITestCase):
    ''' Email preference API test '''
    def setUp(self):
        ''' Set up '''
        user_01 = get_user_model().objects.create_user(username='user_01', password='12345678')
        user_02 = get_user_model().objects.create_user(username='user_02', password='12345678')
        EmailPreference.objects.create(user_id=user_01.id)
        EmailPreference.objects.create(user_id=user_02.id)

    def test_list(self):
        ''' Test list '''
        response = self.client.get('/api/user/email-preference/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_retrieve_own(self):
        ''' Test retrieve own '''
        self.client.login(username='user_01', password='12345678')

        response = self.client.get(
            '/api/user/email-preference/{}/'.format(
                EmailPreference.objects.get(user_id=get_user_model().objects.get(username='user_01').id).id
            )
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.client.logout()

    def test_retrieve_other(self):
        ''' Test retrieve own '''
        self.client.login(username='user_01', password='12345678')

        response = self.client.get(
            '/api/user/email-preference/{}/'.format(
                EmailPreference.objects.get(user_id=get_user_model().objects.get(username='user_02').id).id
            )
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.client.logout()

    def test_create(self):
        ''' Test create '''
        self.client.login(username='user_01', password='12345678')

        response = self.client.post('/api/user/email-preference/', {'user': 1})
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        self.client.logout()

    def test_update_own(self):
        ''' Test update own '''
        self.client.login(username='user_01', password='12345678')

        self.client.patch(
            '/api/user/email-preference/{}/'.format(
                EmailPreference.objects.get(user_id=get_user_model().objects.get(username='user_01').id).id
            ),
            {
                'receive_request': False,
                'receive_announcement': True,
            }
        )
        response = self.client.get(
            '/api/user/email-preference/{}/'.format(
                EmailPreference.objects.get(user_id=get_user_model().objects.get(username='user_01').id).id
            )
        )
        self.assertEqual(response.data['receive_request'], False)
        self.assertEqual(response.data['receive_announcement'], True)

        self.client.logout()

    def test_update_other(self):
        ''' Test update other '''
        self.client.login(username='user_01', password='12345678')

        response = self.client.patch(
            '/api/user/email-preference/{}/'.format(
                EmailPreference.objects.get(user_id=get_user_model().objects.get(username='user_02').id).id
            ),
            {
                'receive_request': False,
                'receive_announcement': True,
            }
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.client.logout()

    def test_delete(self):
        ''' Test delete '''
        self.client.login(username='user_01', password='12345678')

        response = self.client.delete(
            '/api/user/email-preference/{}/'.format(
                EmailPreference.objects.get(user_id=get_user_model().objects.get(username='user_01').id).id
            ),
        )
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        self.client.logout()


class MyEmailPreferenceAPITest(APITestCase):
    ''' User API test '''
    def setUp(self):
        ''' Set up '''
        user_01 = get_user_model().objects.create_user(username='user_01', password='12345678')
        user_02 = get_user_model().objects.create_user(username='user_02', password='12345678')
        EmailPreference.objects.create(user_id=user_01.id)
        EmailPreference.objects.create(user_id=user_02.id)

    def test_retrieve_unauthenticated(self):
        ''' Test retrieve authenticated '''
        response = self.client.get('/api/user/email-preference/me/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_retrieve_authenticated(self):
        ''' Test retrieve authenticated '''
        self.client.login(username='user_01', password='12345678')

        response = self.client.get('/api/user/email-preference/me/')
        self.assertEqual(response.data['user'], get_user_model().objects.get(username='user_01').id)

        self.client.logout()


class StudentCommitteeAuthorityAPITest(APITestCase):
    ''' Student committee authority API test '''
    def setUp(self):
        ''' Set up '''
        user_01 = get_user_model().objects.create_user(username='user_01', password='12345678')
        user_02 = get_user_model().objects.create_user(username='user_02', password='12345678')
        StudentCommitteeAuthority.objects.create(
            user_id=user_01.id, start_date=datetime.now().date(), end_date=datetime.now().date()
        )
        StudentCommitteeAuthority.objects.create(
            user_id=user_02.id, start_date=datetime.now().date(), end_date=datetime.now().date()
        )

    def test_list_unauthenticated(self):
        ''' Test list authenticated '''
        response = self.client.get('/api/user/student-committee/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_authenticated(self):
        ''' Test list authenticated '''
        self.client.login(username='user_01', password='12345678')

        response = self.client.get('/api/user/student-committee/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.client.logout()

    def test_create(self):
        ''' Test create '''
        self.client.login(username='user_01', password='12345678')

        response = self.client.post('/api/user/student-committee/', {})
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        self.client.logout()

    def test_update(self):
        ''' Test update '''
        self.client.login(username='user_01', password='12345678')

        response = self.client.put('/api/user/student-committee/1/', {})
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        response = self.client.patch('/api/user/student-committee/1/', {})
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        self.client.logout()

    def test_delete(self):
        ''' Test delete '''
        self.client.login(username='user_01', password='12345678')

        response = self.client.delete('/api/user/student-committee/1/')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        self.client.logout()


class MyStudentCommitteeAuthorityAPITest(APITestCase):
    ''' My student committee authority API test '''
    def setUp(self):
        ''' Set up '''
        user_01 = get_user_model().objects.create_user(username='user_01', password='12345678')
        user_02 = get_user_model().objects.create_user(username='user_02', password='12345678')
        StudentCommitteeAuthority.objects.create(
            user_id=user_01.id, start_date=datetime.now().date(), end_date=datetime.now().date()
        )
        StudentCommitteeAuthority.objects.create(
            user_id=user_02.id, start_date=datetime.now().date(), end_date=datetime.now().date()
        )

    def test_retrieve_unauthenticated(self):
        ''' Test retrieve authenticated '''
        response = self.client.get('/api/user/student-committee/me/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_retrieve_authenticated(self):
        ''' Test retrieve authenticated '''
        self.client.login(username='user_01', password='12345678')

        response = self.client.get('/api/user/student-committee/me/')
        self.assertEqual(response.data['user'], get_user_model().objects.get(username='user_01').id)

        self.client.logout()
