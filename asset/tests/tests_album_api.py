'''
    Asset Application's Album API Test
    asset/tests/tests_album_api.py
    @author Teerapat Kraisrisirikul (810Teams)
'''

from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from asset.models import Album
from community.models import Club, Event, Lab, CommunityEvent
from membership.models import Membership

import datetime


class AlbumAPITest(APITestCase):
    ''' Album API test '''
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
            name_th='ชุมนุมทดสอบอัลบั้ม สาธารณะ', name_en='Album Testing Club (Public)',
            is_publicly_visible=True, is_official=True
        )
        self.club_private = Club.objects.create(
            name_th='ชุมนุมทดสอบอัลบั้ม ส่วนตัว', name_en='Album Testing Club (Private)',
            is_publicly_visible=False, is_official=False
        )
        self.event = Event.objects.create(
            name_th='กิจกรรมทดสอบอัลบั้ม', name_en='Album Testing Event',
            is_approved=True, location='L207 IT KMITL',
            start_date=datetime.date(2020, 12, 1), end_date=datetime.date(2020, 12, 2),
            start_time=datetime.time(9, 0, 0), end_time=datetime.time(17, 0, 0), is_publicly_visible=False
        )
        self.lab = Lab.objects.create(name_th='ห้องปฏิบัติการทดสอบอัลบั้ม', name_en='Album Testing Lab')
        self.club_event = CommunityEvent.objects.create(
            name_th='กิจกรรมชุมนุมทดสอบอัลบั้ม', name_en='Album Testing Club Event',
            is_approved=True, location='L207 IT KMITL',
            start_date=datetime.date(2020, 12, 1), end_date=datetime.date(2020, 12, 2),
            start_time=datetime.time(9, 0, 0), end_time=datetime.time(17, 0, 0),
            created_under_id=self.club_public.id, is_publicly_visible=False
        )
        self.lab_event = CommunityEvent.objects.create(
            name_th='กิจกรรมห้องปฏิบัติการทดสอบอัลบั้ม', name_en='Album Testing Lab Event',
            is_approved=True, location='L207 IT KMITL',
            start_date=datetime.date(2020, 12, 1), end_date=datetime.date(2020, 12, 2),
            start_time=datetime.time(9, 0, 0), end_time=datetime.time(17, 0, 0),
            created_under_id=self.lab.id, is_publicly_visible=False
        )

        Membership.objects.create(community_id=self.club_public.id, user_id=self.user_01.id, position=3)
        Membership.objects.create(community_id=self.club_public.id, user_id=self.user_02.id, position=2)
        Membership.objects.create(community_id=self.club_public.id, user_id=self.user_03.id, position=1)
        Membership.objects.create(community_id=self.club_public.id, user_id=self.user_04.id, position=0)

        Membership.objects.create(community_id=self.club_private.id, user_id=self.user_01.id, position=3)
        Membership.objects.create(community_id=self.club_private.id, user_id=self.user_02.id, position=2)
        Membership.objects.create(community_id=self.club_private.id, user_id=self.user_03.id, position=1)
        Membership.objects.create(community_id=self.club_private.id, user_id=self.user_04.id, position=0)

        Membership.objects.create(community_id=self.event.id, user_id=self.user_01.id, position=3)
        Membership.objects.create(community_id=self.event.id, user_id=self.user_02.id, position=2)
        Membership.objects.create(community_id=self.event.id, user_id=self.user_03.id, position=1)
        Membership.objects.create(community_id=self.event.id, user_id=self.user_04.id, position=0)

        Membership.objects.create(community_id=self.club_event.id, user_id=self.user_01.id, position=3)
        Membership.objects.create(community_id=self.club_event.id, user_id=self.user_02.id, position=2)
        Membership.objects.create(community_id=self.club_event.id, user_id=self.user_03.id, position=1)
        Membership.objects.create(community_id=self.club_event.id, user_id=self.user_04.id, position=0)

        Membership.objects.create(community_id=self.lab.id, user_id=self.lecturer_01.id, position=3)
        Membership.objects.create(community_id=self.lab.id, user_id=self.lecturer_02.id, position=2)
        Membership.objects.create(community_id=self.lab.id, user_id=self.user_03.id, position=1)
        Membership.objects.create(community_id=self.lab.id, user_id=self.user_04.id, position=0)

    def test_list_album_authenticated(self):
        ''' Test list album while authenticated '''
        self.client.login(username='user_05', password='12345678')

        Album.objects.create(community_id=self.club_public.id, name='My Album 1')
        Album.objects.create(community_id=self.club_private.id, name='My Album 2')
        response = self.client.get('/api/asset/album/')
        self.assertEqual(len(response.data), 2)

        self.client.logout()

    def test_list_album_unauthenticated(self):
        ''' Test list album while unauthenticated '''
        Album.objects.create(community_id=self.club_public.id, name='My Album 1')
        Album.objects.create(community_id=self.club_private.id, name='My Album 2')
        response = self.client.get('/api/asset/album/')
        self.assertEqual(len(response.data), 1)

    def test_retrieve_album_as_leader(self):
        ''' Test retrieve album as leader '''
        album = Album.objects.create(community_id=self.club_public.id, is_publicly_visible=True, name='My Album 1')
        self._test_retrieve_album_as(username='user_01', album_id=album.id, allows_retrieve=True)

        album = Album.objects.create(community_id=self.club_public.id, is_publicly_visible=False, name='My Album 2')
        self._test_retrieve_album_as(username='user_01', album_id=album.id, allows_retrieve=True)

        album = Album.objects.create(community_id=self.club_private.id, is_publicly_visible=True, name='My Album 3')
        self._test_retrieve_album_as(username='user_01', album_id=album.id, allows_retrieve=True)

        album = Album.objects.create(community_id=self.club_private.id, is_publicly_visible=False, name='My Album 4')
        self._test_retrieve_album_as(username='user_01', album_id=album.id, allows_retrieve=True)

    def test_retrieve_album_as_deputy_leader(self):
        ''' Test retrieve album as deputy leader '''
        album = Album.objects.create(community_id=self.club_public.id, is_publicly_visible=True, name='My Album 1')
        self._test_retrieve_album_as(username='user_02', album_id=album.id, allows_retrieve=True)

        album = Album.objects.create(community_id=self.club_public.id, is_publicly_visible=False, name='My Album 2')
        self._test_retrieve_album_as(username='user_02', album_id=album.id, allows_retrieve=True)

        album = Album.objects.create(community_id=self.club_private.id, is_publicly_visible=True, name='My Album 3')
        self._test_retrieve_album_as(username='user_02', album_id=album.id, allows_retrieve=True)

        album = Album.objects.create(community_id=self.club_private.id, is_publicly_visible=False, name='My Album 4')
        self._test_retrieve_album_as(username='user_03', album_id=album.id, allows_retrieve=True)

    def test_retrieve_album_as_staff(self):
        ''' Test retrieve album as staff  '''
        album = Album.objects.create(community_id=self.club_public.id, is_publicly_visible=True, name='My Album 1')
        self._test_retrieve_album_as(username='user_03', album_id=album.id, allows_retrieve=True)

        album = Album.objects.create(community_id=self.club_public.id, is_publicly_visible=False, name='My Album 2')
        self._test_retrieve_album_as(username='user_03', album_id=album.id, allows_retrieve=True)

        album = Album.objects.create(community_id=self.club_private.id, is_publicly_visible=True, name='My Album 3')
        self._test_retrieve_album_as(username='user_03', album_id=album.id, allows_retrieve=True)

        album = Album.objects.create(community_id=self.club_private.id, is_publicly_visible=False, name='My Album 4')
        self._test_retrieve_album_as(username='user_03', album_id=album.id, allows_retrieve=True)

    def test_retrieve_album_as_member(self):
        ''' Test retrieve album as member '''
        album = Album.objects.create(community_id=self.club_public.id, is_publicly_visible=True, name='My Album 1')
        self._test_retrieve_album_as(username='user_04', album_id=album.id, allows_retrieve=True)

        album = Album.objects.create(community_id=self.club_public.id, is_publicly_visible=False, name='My Album 2')
        self._test_retrieve_album_as(username='user_04', album_id=album.id, allows_retrieve=True)

        album = Album.objects.create(community_id=self.club_private.id, is_publicly_visible=True, name='My Album 3')
        self._test_retrieve_album_as(username='user_04', album_id=album.id, allows_retrieve=True)

        album = Album.objects.create(community_id=self.club_private.id, is_publicly_visible=False, name='My Album 4')
        self._test_retrieve_album_as(username='user_04', album_id=album.id, allows_retrieve=True)

    def test_retrieve_album_as_non_member(self):
        ''' Test retrieve album as non-member '''
        album = Album.objects.create(community_id=self.club_public.id, is_publicly_visible=True, name='My Album 1')
        self._test_retrieve_album_as(username='user_05', album_id=album.id, allows_retrieve=True)

        album = Album.objects.create(community_id=self.club_public.id, is_publicly_visible=False, name='My Album 2')
        self._test_retrieve_album_as(username='user_05', album_id=album.id, allows_retrieve=False)

        album = Album.objects.create(community_id=self.club_private.id, is_publicly_visible=True, name='My Album 3')
        self._test_retrieve_album_as(username='user_05', album_id=album.id, allows_retrieve=True)

        album = Album.objects.create(community_id=self.club_private.id, is_publicly_visible=False, name='My Album 4')
        self._test_retrieve_album_as(username='user_05', album_id=album.id, allows_retrieve=False)

    def test_retrieve_album_as_guest(self):
        ''' Test retrieve album as guest '''
        album = Album.objects.create(community_id=self.club_public.id, is_publicly_visible=True, name='My Album 1')
        self._test_retrieve_album_as(album_id=album.id, allows_retrieve=True)

        album = Album.objects.create(community_id=self.club_public.id, is_publicly_visible=False, name='My Album 2')
        self._test_retrieve_album_as(album_id=album.id, allows_retrieve=False)

        album = Album.objects.create(community_id=self.club_private.id, is_publicly_visible=True, name='My Album 3')
        self._test_retrieve_album_as(album_id=album.id, allows_retrieve=False)

        album = Album.objects.create(community_id=self.club_private.id, is_publicly_visible=False, name='My Album 4')
        self._test_retrieve_album_as(album_id=album.id, allows_retrieve=False)

    def test_retrieve_album_as_community_event_member_alone(self):
        ''' Test retrieve album as a member of the community event alone but not its parent community '''
        album = Album.objects.create(
            community_id=self.club_public.id, community_event_id=self.club_event.id,
            is_publicly_visible=True, name='My Album 1'
        )
        self._test_retrieve_album_as(username='user_05', album_id=album.id, allows_retrieve=True)

        album = Album.objects.create(
            community_id=self.club_public.id, community_event_id=self.club_event.id,
            is_publicly_visible=False, name='My Album 2'
        )
        self._test_retrieve_album_as(username='user_05', album_id=album.id, allows_retrieve=False)

        Membership.objects.create(user_id=self.user_05.id, community_id=self.club_event.id)

        album = Album.objects.create(
            community_id=self.club_public.id, community_event_id=self.club_event.id,
            is_publicly_visible=True, name='My Album 3'
        )
        self._test_retrieve_album_as(username='user_05', album_id=album.id, allows_retrieve=True)

        album = Album.objects.create(
            community_id=self.club_public.id, community_event_id=self.club_event.id,
            is_publicly_visible=False, name='My Album 4'
        )
        self._test_retrieve_album_as(username='user_05', album_id=album.id, allows_retrieve=True)

    def _test_retrieve_album_as(self, username=str(), album_id=None, allows_retrieve=True):
        ''' Test retrieve album as different membership positions '''
        if username.strip() != str():
            self.client.login(username=username, password='12345678')

        response = self.client.get('/api/asset/album/{}/'.format(album_id))

        if allows_retrieve:
            self.assertEqual(response.status_code, status.HTTP_200_OK)
        else:
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        if username.strip() != str():
            self.client.logout()

    def test_create_album_as_leader(self):
        ''' Test create album as leader '''
        self._test_create_album_as('user_01', allows_create=True)

    def test_create_album_as_deputy_leader(self):
        ''' Test create album as deputy leader '''
        self._test_create_album_as('user_02', allows_create=True)

    def test_create_album_as_staff(self):
        ''' Test create album as staff '''
        self._test_create_album_as('user_03', allows_create=True)

    def test_create_album_as_member(self):
        ''' Test create album as member '''
        self._test_create_album_as('user_04', allows_create=False)

    def test_create_album_as_non_member(self):
        ''' Test create album as non-member '''
        self._test_create_album_as('user_05', allows_create=False)

    def test_create_album_as_guest(self):
        ''' Test create album as guest '''
        self._test_create_album_as(str(), allows_create=False)

    def _test_create_album_as(self, username=str(), allows_create=True):
        ''' Test create album as different membership positions '''
        if username.strip() != str():
            self.client.login(username=username, password='12345678')

        response = self.client.post('/api/asset/album/', {
            'name': 'My Album',
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

    def test_create_album_under_club(self):
        ''' Test create album under club '''
        self._test_create_album_under('user_01', community_id=self.club_public.id, allows_create=True)

    def test_create_album_under_event(self):
        ''' Test create album under event '''
        self._test_create_album_under('user_01', community_id=self.event.id, allows_create=True)

    def test_create_album_under_community_event(self):
        ''' Test create album under community event '''
        self._test_create_album_under(username='user_01', community_id=self.club_event.id, allows_create=False)
        self._test_create_album_under(username='lecturer_01', community_id=self.lab_event.id, allows_create=False)

    def test_create_album_under_lab(self):
        ''' Test create album under lab '''
        self._test_create_album_under('lecturer_01', community_id=self.lab.id, allows_create=True)

    def _test_create_album_under(self, username=str(), community_id=int(), allows_create=True):
        ''' Test create album under different community types '''
        self.client.login(username=username, password='12345678')

        response = self.client.post('/api/asset/album/', {
            'name': 'My Album',
            'community': community_id
        })

        if allows_create:
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        else:
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.client.logout()

    def test_update_album_as_leader(self):
        ''' Test update album as leader '''
        self._test_update_album_as('user_01', allows_update=True)

    def test_update_album_as_deputy_leader(self):
        ''' Test update album as deputy leader '''
        self._test_update_album_as('user_02', allows_update=True)

    def test_update_album_as_staff(self):
        ''' Test update album as staff '''
        self._test_update_album_as('user_03', allows_update=True)

    def test_update_album_as_member(self):
        ''' Test update album as member '''
        self._test_update_album_as('user_04', allows_update=False)

    def test_update_album_as_non_member(self):
        ''' Test update album as non-member '''
        self._test_update_album_as('user_05', allows_update=False)

    def test_update_album_as_guest(self):
        ''' Test update album as guest '''
        self._test_update_album_as(str(), allows_update=False)

    def _test_update_album_as(self, username=str(), allows_update=True):
        ''' Test create album as different membership positions '''
        if username.strip() != str():
            self.client.login(username=username, password='12345678')

        album = Album.objects.create(community_id=self.club_public.id, name='My Album')
        response = self.client.patch('/api/asset/album/{}/'.format(album.id), {
            'name': 'My Photo Collection'
        })

        if allows_update:
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(Album.objects.get(pk=album.id).name, 'My Photo Collection')
        else:
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
            self.assertEqual(Album.objects.get(pk=album.id).name, 'My Album')

        if username.strip() != str():
            self.client.logout()

    def test_link_album_to_own_community_event(self):
        ''' Test link album to own community events '''
        self._test_link_album_to(
            username='user_01', community_id=self.club_public.id,
            community_event_id=self.club_event.id, allows_update=True
        )
        self._test_link_album_to(
            username='lecturer_01', community_id=self.lab.id,
            community_event_id=self.lab_event.id, allows_update=True
        )

    def test_link_album_to_other_community_event(self):
        ''' Test link album to other community events '''
        self._test_link_album_to(
            username='user_01', community_id=self.club_public.id,
            community_event_id=self.lab_event.id, allows_update=False
        )
        self._test_link_album_to(
            username='lecturer_01', community_id=self.lab.id,
            community_event_id=self.club_event.id, allows_update=False
        )

    def test_link_album_to_non_community_events(self):
        ''' Test link album to non-community events '''
        self._test_link_album_to(
            username='user_01', community_id=self.club_public.id,
            community_event_id=self.club_public.id, allows_update=False
        )
        self._test_link_album_to(
            username='user_01', community_id=self.club_public.id,
            community_event_id=self.club_private.id, allows_update=False
        )
        self._test_link_album_to(
            username='user_01', community_id=self.club_public.id,
            community_event_id=self.event.id, allows_update=False
        )
        self._test_link_album_to(
            username='user_01', community_id=self.club_public.id,
            community_event_id=self.lab.id, allows_update=False
        )
        self._test_link_album_to(
            username='lecturer_01', community_id=self.lab.id,
            community_event_id=self.club_public.id, allows_update=False
        )
        self._test_link_album_to(
            username='lecturer_01', community_id=self.lab.id,
            community_event_id=self.club_private.id, allows_update=False
        )
        self._test_link_album_to(
            username='lecturer_01', community_id=self.lab.id,
            community_event_id=self.event.id, allows_update=False
        )
        self._test_link_album_to(
            username='lecturer_01', community_id=self.lab.id,
            community_event_id=self.lab.id, allows_update=False
        )

    def _test_link_album_to(self, username=str(), community_id=int(), community_event_id=int(), allows_update=True):
        ''' Test link album to different community events '''
        self.client.login(username=username, password='12345678')

        album = Album.objects.create(community_id=community_id, name='My Album')
        response = self.client.patch('/api/asset/album/{}/'.format(album.id), {
            'community_event': community_event_id
        })

        if allows_update:
            self.assertEqual(response.status_code, status.HTTP_200_OK)
        else:
            self.assertIn(response.status_code, (status.HTTP_400_BAD_REQUEST, status.HTTP_403_FORBIDDEN))

        self.client.logout()

    def test_delete_album_as_leader(self):
        ''' Test delete album as leader '''
        self._test_delete_album_as('user_01', allows_delete=True)

    def test_delete_album_as_deputy_leader(self):
        ''' Test delete album as deputy leader '''
        self._test_delete_album_as('user_02', allows_delete=True)

    def test_delete_album_as_staff(self):
        ''' Test delete album as staff '''
        self._test_delete_album_as('user_03', allows_delete=True)

    def test_delete_album_as_member(self):
        ''' Test delete album as member '''
        self._test_delete_album_as('user_04', allows_delete=False)

    def test_delete_album_as_non_member(self):
        ''' Test delete album as non-member '''
        self._test_delete_album_as('user_05', allows_delete=False)

    def test_delete_album_as_guest(self):
        ''' Test delete album as guest '''
        self._test_delete_album_as(str(), allows_delete=False)

    def _test_delete_album_as(self, username=str(), allows_delete=True):
        ''' Test delete album as different membership positions '''
        if username.strip() != str():
            self.client.login(username=username, password='12345678')

        album = Album.objects.create(community_id=self.club_public.id, name='My Album')
        response = self.client.delete('/api/asset/album/{}/'.format(album.id))

        if allows_delete:
            self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        else:
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        if username.strip() != str():
            self.client.logout()
