'''
    Asset Application's Announcement API Test
    asset/tests/tests_announcement_api.py
    @author Teerapat Kraisrisirikul (810Teams)
'''

from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from asset.models import Announcement
from community.models import Club
from membership.models import Membership


class AnnouncementAPITest(APITestCase):
    ''' Announcement API test '''
    def setUp(self):
        ''' Set up '''
        self.user_01 = get_user_model().objects.create_user(username='user_01', password='12345678', name='User One')
        self.user_02 = get_user_model().objects.create_user(username='user_02', password='12345678', name='User Two')
        self.user_03 = get_user_model().objects.create_user(username='user_03', password='12345678', name='User Three')
        self.user_04 = get_user_model().objects.create_user(username='user_04', password='12345678', name='User Four')
        self.user_05 = get_user_model().objects.create_user(username='user_05', password='12345678', name='User Five')
        self.lecturer_01 = get_user_model().objects.create_user(
            username='lecturer_01', password='12345678', name='Prof.Lazy Bones', user_group='lecturer'
        )
        self.lecturer_02 = get_user_model().objects.create_user(
            username='lecturer_02', password='12345678', name='Prof.Lazy Ass', user_group='lecturer'
        )
        self.club_public = Club.objects.create(
            name_th='ชุมนุมทดสอบประกาศ สาธารณะ', name_en='Announcement Testing Club (Public)',
            is_publicly_visible=True, is_official=True
        )
        self.club_private = Club.objects.create(
            name_th='ชุมนุมทดสอบประกาศ ส่วนตัว', name_en='Announcement Testing Club (Private)',
            is_publicly_visible=False, is_official=False
        )

        Membership.objects.create(community_id=self.club_public.id, user_id=self.user_01.id, position=3)
        Membership.objects.create(community_id=self.club_public.id, user_id=self.user_02.id, position=2)
        Membership.objects.create(community_id=self.club_public.id, user_id=self.user_03.id, position=1)
        Membership.objects.create(community_id=self.club_public.id, user_id=self.user_04.id, position=0)

        Membership.objects.create(community_id=self.club_private.id, user_id=self.user_01.id, position=3)
        Membership.objects.create(community_id=self.club_private.id, user_id=self.user_02.id, position=2)
        Membership.objects.create(community_id=self.club_private.id, user_id=self.user_03.id, position=1)
        Membership.objects.create(community_id=self.club_private.id, user_id=self.user_04.id, position=0)

    def test_list_announcement_authenticated(self):
        ''' Test list announcement while authenticated '''
        self.client.login(username='user_05', password='12345678')

        Announcement.objects.create(community_id=self.club_public.id, text='Greetings')
        Announcement.objects.create(community_id=self.club_private.id, text='Greetings')
        response = self.client.get('/api/asset/announcement/')
        self.assertEqual(len(response.data), 2)

        self.client.logout()

    def test_list_announcement_unauthenticated(self):
        ''' Test list announcement while unauthenticated '''
        Announcement.objects.create(community_id=self.club_public.id, text='Greetings')
        Announcement.objects.create(community_id=self.club_private.id, text='Greetings')
        response = self.client.get('/api/asset/announcement/')
        self.assertEqual(len(response.data), 1)

    def test_list_announcement_as_member(self):
        ''' Test list announcement as member '''
        self.client.login(username='user_04', password='12345678')

        Announcement.objects.create(community_id=self.club_public.id, text='Greetings', is_publicly_visible=True)
        Announcement.objects.create(community_id=self.club_public.id, text='Greetings', is_publicly_visible=False)
        response = self.client.get('/api/asset/announcement/')
        self.assertEqual(len(response.data), 2)

        self.client.logout()

    def test_list_announcement_as_non_member(self):
        ''' Test list announcement as non-member '''
        self.client.login(username='user_05', password='12345678')

        Announcement.objects.create(community_id=self.club_public.id, text='Greetings', is_publicly_visible=True)
        Announcement.objects.create(community_id=self.club_public.id, text='Greetings', is_publicly_visible=False)
        response = self.client.get('/api/asset/announcement/')
        self.assertEqual(len(response.data), 1)

        self.client.logout()

    def test_retrieve_announcement_authenticated(self):
        ''' Test retrieve announcement while authenticated '''
        self.client.login(username='user_05', password='12345678')

        announcement = Announcement.objects.create(community_id=self.club_public.id, text='Greetings')
        response = self.client.get('/api/asset/announcement/{}/'.format(announcement.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        announcement = Announcement.objects.create(community_id=self.club_private.id, text='Greetings')
        response = self.client.get('/api/asset/announcement/{}/'.format(announcement.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.client.logout()

    def test_retrieve_announcement_unauthenticated(self):
        ''' Test retrieve announcement while unauthenticated '''
        announcement = Announcement.objects.create(community_id=self.club_public.id, text='Greetings')
        response = self.client.get('/api/asset/announcement/{}/'.format(announcement.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        announcement = Announcement.objects.create(community_id=self.club_private.id, text='Greetings')
        response = self.client.get('/api/asset/announcement/{}/'.format(announcement.id))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_retrieve_announcement_as_member(self):
        ''' Test retrieve announcement as member '''
        self.client.login(username='user_04', password='12345678')

        announcement = Announcement.objects.create(
            community_id=self.club_public.id, text='Greetings', is_publicly_visible=True
        )
        response = self.client.get('/api/asset/announcement/{}/'.format(announcement.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        announcement = Announcement.objects.create(
            community_id=self.club_private.id, text='Greetings', is_publicly_visible=False
        )
        response = self.client.get('/api/asset/announcement/{}/'.format(announcement.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.client.logout()

    def test_retrieve_announcement_as_non_member(self):
        ''' Test retrieve announcement as non-member '''
        self.client.login(username='user_05', password='12345678')

        announcement = Announcement.objects.create(
            community_id=self.club_public.id, text='Greetings', is_publicly_visible=True
        )
        response = self.client.get('/api/asset/announcement/{}/'.format(announcement.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        announcement = Announcement.objects.create(
            community_id=self.club_private.id, text='Greetings', is_publicly_visible=False
        )
        response = self.client.get('/api/asset/announcement/{}/'.format(announcement.id))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.client.logout()

    def test_create_announcement_as_leader(self):
        ''' Test create announcement as leader '''
        self._test_create_announcement_as('user_01', allows_create=True)

    def test_create_announcement_as_deputy_leader(self):
        ''' Test create announcement as deputy leader '''
        self._test_create_announcement_as('user_02', allows_create=True)

    def test_create_announcement_as_staff(self):
        ''' Test create announcement as staff '''
        self._test_create_announcement_as('user_03', allows_create=True)

    def test_create_announcement_as_member(self):
        ''' Test create announcement as member '''
        self._test_create_announcement_as('user_04', allows_create=False)

    def test_create_announcement_as_non_member(self):
        ''' Test create announcement as non-member '''
        self._test_create_announcement_as('user_05', allows_create=False)

    def test_create_announcement_as_guest(self):
        ''' Test create announcement as guest '''
        self._test_create_announcement_as(str(), allows_create=False)

    def _test_create_announcement_as(self, username=str(), allows_create=True):
        ''' Test create announcement as different membership positions '''
        if username.strip() != str():
            self.client.login(username=username, password='12345678')

        response = self.client.post('/api/asset/announcement/', {
            'text': 'Greetings',
            'community': self.club_public.id
        })

        if allows_create:
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        elif username.strip() == str():
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        else:
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        if username.strip() != str():
            self.client.logout()

    def test_update_announcement_as_leader(self):
        ''' Test update announcement as leader '''
        self._test_update_announcement_as('user_01', allows_update=True)

    def test_update_announcement_as_deputy_leader(self):
        ''' Test update announcement as deputy leader '''
        self._test_update_announcement_as('user_02', allows_update=True)

    def test_update_announcement_as_staff(self):
        ''' Test update announcement as staff '''
        self._test_update_announcement_as('user_03', allows_update=True)

    def test_update_announcement_as_member(self):
        ''' Test update announcement as member '''
        self._test_update_announcement_as('user_04', allows_update=False)

    def test_update_announcement_as_non_member(self):
        ''' Test update announcement as non-member '''
        self._test_update_announcement_as('user_05', allows_update=False)

    def test_update_announcement_as_guest(self):
        ''' Test update announcement as guest '''
        self._test_update_announcement_as(str(), allows_update=False)

    def _test_update_announcement_as(self, username=str(), allows_update=True):
        ''' Test create announcement as different membership positions '''
        if username.strip() != str():
            self.client.login(username=username, password='12345678')

        announcement = Announcement.objects.create(community_id=self.club_public.id, text='Greetings')
        response = self.client.patch('/api/asset/announcement/{}/'.format(announcement.id), {
            'text': 'Merry Christmas',
        })

        if allows_update:
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(Announcement.objects.get(pk=announcement.id).text, 'Merry Christmas')
        else:
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
            self.assertEqual(Announcement.objects.get(pk=announcement.id).text, 'Greetings')

        if username.strip() != str():
            self.client.logout()

    def test_delete_announcement_as_leader(self):
        ''' Test delete announcement as leader '''
        self._test_delete_announcement_as('user_01', allows_delete=True)

    def test_delete_announcement_as_deputy_leader(self):
        ''' Test delete announcement as deputy leader '''
        self._test_delete_announcement_as('user_02', allows_delete=True)

    def test_delete_announcement_as_staff(self):
        ''' Test delete announcement as staff '''
        self._test_delete_announcement_as('user_03', allows_delete=True)

    def test_delete_announcement_as_member(self):
        ''' Test delete announcement as member '''
        self._test_delete_announcement_as('user_04', allows_delete=False)

    def test_delete_announcement_as_non_member(self):
        ''' Test delete announcement as non-member '''
        self._test_delete_announcement_as('user_05', allows_delete=False)

    def test_delete_announcement_as_guest(self):
        ''' Test delete announcement as guest '''
        self._test_delete_announcement_as(str(), allows_delete=False)

    def _test_delete_announcement_as(self, username=str(), allows_delete=True):
        ''' Test delete announcement as different membership positions '''
        if username.strip() != str():
            self.client.login(username=username, password='12345678')

        announcement = Announcement.objects.create(community_id=self.club_public.id, text='Greetings')
        response = self.client.delete('/api/asset/announcement/{}/'.format(announcement.id))

        if allows_delete:
            self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        else:
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        if username.strip() != str():
            self.client.logout()
