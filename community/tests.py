'''
    Community Application Tests
    community/tests.py
    @author Teerapat Kraisrisirikul (810Teams)
'''

from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from community.models import Community, Club, Event, CommunityEvent, Lab
from core.utils.general import get_random_string
from membership.models import Membership

import datetime


class CommunityAPITest(APITestCase):
    ''' Community API test '''
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
        self.support_staff = get_user_model().objects.create_user(
            username='support', password='12345678', name='Mr.Supporter', user_group='support'
        )

        self.club_public = Club.objects.create(
            name_th='ชุมนุมทดสอบสังคม สาธารณะ', name_en='Community Testing Club (Public)',
            is_publicly_visible=True, is_official=True
        )
        self.club_private = Club.objects.create(
            name_th='ชุมนุมทดสอบสังคม ส่วนตัว', name_en='Community Testing Club (Private)',
            is_publicly_visible=False, is_official=False
        )
        self.event = Event.objects.create(
            name_th='กิจกรรมทดสอบสังคม',
            name_en='Advisory Testing Event',
            is_approved=True,
            location='L207 IT KMITL',
            start_date=datetime.date(2020, 12, 1),
            end_date=datetime.date(2020, 12, 2),
            start_time=datetime.time(9, 0, 0),
            end_time=datetime.time(17, 0, 0),
            is_publicly_visible=False
        )
        self.lab = Lab.objects.create(name_th='ห้องปฏิบัติการทดสอบสังคม', name_en='Community Testing Lab')
        self.community_event = CommunityEvent.objects.create(
            name_th='กิจกรรมชุมนุมทดสอบสังคม',
            name_en='Community Testing Club Event',
            is_approved=True,
            location='L207 IT KMITL',
            start_date=datetime.date(2020, 12, 1),
            end_date=datetime.date(2020, 12, 2),
            start_time=datetime.time(9, 0, 0),
            end_time=datetime.time(17, 0, 0),
            created_under_id=self.club_public.id,
            is_publicly_visible=False
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

        Membership.objects.create(community_id=self.community_event.id, user_id=self.user_01.id, position=3)
        Membership.objects.create(community_id=self.community_event.id, user_id=self.user_02.id, position=2)
        Membership.objects.create(community_id=self.community_event.id, user_id=self.user_03.id, position=1)
        Membership.objects.create(community_id=self.community_event.id, user_id=self.user_04.id, position=0)

        Membership.objects.create(community_id=self.lab.id, user_id=self.lecturer_01.id, position=3)
        Membership.objects.create(community_id=self.lab.id, user_id=self.lecturer_02.id, position=2)
        Membership.objects.create(community_id=self.lab.id, user_id=self.user_03.id, position=1)
        Membership.objects.create(community_id=self.lab.id, user_id=self.user_04.id, position=0)

    def test_list_community_authenticated(self):
        ''' Test list community authenticated '''
        self.client.login(username='user_05', password='12345678')

        self._test_list_community(instance_path='club', expected_length=2)
        self._test_list_community(instance_path='event', expected_length=2)
        self._test_list_community(instance_path='event/community', expected_length=1)
        self._test_list_community(instance_path='lab', expected_length=1)

        self.client.logout()

    def test_list_community_unauthenticated(self):
        ''' Test list community unauthenticated '''
        self._test_list_community(instance_path='club', expected_length=1)
        self._test_list_community(instance_path='event', expected_length=0)
        self._test_list_community(instance_path='event/community', expected_length=0)
        self._test_list_community(instance_path='lab', expected_length=0)

    def _test_list_community(self, instance_path='club', expected_length=0):
        ''' Test list community '''
        response = self.client.get('/api/community/{}/'.format(instance_path))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), expected_length)

    def test_retrieve_community_authenticated(self):
        ''' Test retrieve community authenticated '''
        self.client.login(username='user_05', password='12345678')

        self._test_retrieve_community(instance_path='club', instance_id=self.club_public.id, allows_retrieve=True)
        self._test_retrieve_community(instance_path='club', instance_id=self.club_private.id, allows_retrieve=True)
        self._test_retrieve_community(instance_path='event', instance_id=self.event.id, allows_retrieve=True)
        self._test_retrieve_community(
            instance_path='event/community', instance_id=self.community_event.id, allows_retrieve=True
        )
        self._test_retrieve_community(instance_path='lab', instance_id=self.lab.id, allows_retrieve=True)

        self.client.logout()

    def test_retrieve_community_unauthenticated(self):
        ''' Test retrieve community unauthenticated '''
        self._test_retrieve_community(instance_path='club', instance_id=self.club_public.id, allows_retrieve=True)
        self._test_retrieve_community(instance_path='club', instance_id=self.club_private.id, allows_retrieve=False)
        self._test_retrieve_community(instance_path='event', instance_id=self.event.id, allows_retrieve=False)
        self._test_retrieve_community(
            instance_path='event/community', instance_id=self.community_event.id, allows_retrieve=False
        )
        self._test_retrieve_community(instance_path='lab', instance_id=self.lab.id, allows_retrieve=False)

    def _test_retrieve_community(self, instance_path='club', instance_id=0, allows_retrieve=False):
        ''' Test retrieve community '''
        response = self.client.get('/api/community/{}/{}/'.format(instance_path, instance_id))

        if allows_retrieve:
            self.assertEqual(response.status_code, status.HTTP_200_OK)
        else:
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_retrieve_community_event_under_non_publicly_visible_community(self):
        ''' Test retrieve community event under non-publicly visible community '''
        club = Club.objects.create(
            name_th='ชุมนุมนอน', name_en='Sleeping Club', is_publicly_visible=False, is_official=True
        )
        community_event = CommunityEvent.objects.create(
            name_th='นิทรรศการเตียงนอน',
            name_en='Bed Fair',
            is_approved=True,
            location='Somewhere undecided',
            start_date=datetime.date(2020, 12, 1),
            end_date=datetime.date(2020, 12, 2),
            start_time=datetime.time(9, 0, 0),
            end_time=datetime.time(17, 0, 0),
            created_under_id=club.id,
            is_publicly_visible=True
        )

        # Unauthenticated
        response = self.client.get('/api/community/club/{}/'.format(club.id))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        response = self.client.get('/api/community/event/community/{}/'.format(community_event.id))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Authenticated
        self.client.login(username='user_05', password='12345678')

        response = self.client.get('/api/community/club/{}/'.format(club.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.get('/api/community/event/community/{}/'.format(community_event.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.client.logout()

    def test_create_club(self):
        ''' Test create club '''
        self._test_create_community(username='user_05', instance_path='club', allows_create=True)
        self._test_create_community(username='lecturer_02', instance_path='club', allows_create=False)
        self._test_create_community(username='support', instance_path='club', allows_create=False)
        self._test_create_community(username=str(), instance_path='club', allows_create=False)

    def test_create_event(self):
        ''' Test create event '''
        self._test_create_community(username='user_05', instance_path='event', allows_create=True)
        self._test_create_community(username='lecturer_01', instance_path='event', allows_create=True)
        self._test_create_community(username='support', instance_path='event', allows_create=True)
        self._test_create_community(username=str(), instance_path='event', allows_create=False)

    def test_create_community_event_under_official_club(self):
        ''' Test create community event under official club '''
        self._test_create_community(
            username='user_01', instance_path='event/community', created_under=self.club_public.id, allows_create=True
        )
        self._test_create_community(
            username='user_02', instance_path='event/community', created_under=self.club_public.id, allows_create=True
        )
        self._test_create_community(
            username='user_03', instance_path='event/community', created_under=self.club_public.id, allows_create=True
        )
        self._test_create_community(
            username='user_04', instance_path='event/community', created_under=self.club_public.id, allows_create=False
        )
        self._test_create_community(
            username='user_05', instance_path='event/community', created_under=self.club_public.id, allows_create=False
        )
        self._test_create_community(
            username=str(), instance_path='event/community', created_under=self.club_public.id, allows_create=False
        )

    def test_create_community_event_under_unofficial_club(self):
        ''' Test create community event under unofficial club '''
        self._test_create_community(
            username='user_01', instance_path='event/community', created_under=self.club_private.id, allows_create=False
        )
        self._test_create_community(
            username='user_02', instance_path='event/community', created_under=self.club_private.id, allows_create=False
        )
        self._test_create_community(
            username='user_03', instance_path='event/community', created_under=self.club_private.id, allows_create=False
        )
        self._test_create_community(
            username='user_04', instance_path='event/community', created_under=self.club_private.id, allows_create=False
        )
        self._test_create_community(
            username='user_05', instance_path='event/community', created_under=self.club_private.id, allows_create=False
        )
        self._test_create_community(
            username=str(), instance_path='event/community', created_under=self.club_private.id, allows_create=False
        )

    def test_create_community_event_under_event(self):
        ''' Test create community event under event '''
        self._test_create_community(
            username='user_01', instance_path='event/community', created_under=self.event.id, allows_create=False
        )
        self._test_create_community(
            username='user_02', instance_path='event/community', created_under=self.event.id, allows_create=False
        )
        self._test_create_community(
            username='user_03', instance_path='event/community', created_under=self.event.id, allows_create=False
        )
        self._test_create_community(
            username='user_04', instance_path='event/community', created_under=self.event.id, allows_create=False
        )
        self._test_create_community(
            username='user_05', instance_path='event/community', created_under=self.event.id, allows_create=False
        )
        self._test_create_community(
            username=str(), instance_path='event/community', created_under=self.event.id, allows_create=False
        )

    def test_create_community_event_under_community_event(self):
        ''' Test create community event under event '''
        self._test_create_community(
            username='user_01', instance_path='event/community',
            created_under=self.community_event.id, allows_create=False
        )
        self._test_create_community(
            username='user_02', instance_path='event/community',
            created_under=self.community_event.id, allows_create=False
        )
        self._test_create_community(
            username='user_03', instance_path='event/community',
            created_under=self.community_event.id, allows_create=False
        )
        self._test_create_community(
            username='user_04', instance_path='event/community',
            created_under=self.community_event.id, allows_create=False
        )
        self._test_create_community(
            username='user_05', instance_path='event/community',
            created_under=self.community_event.id, allows_create=False
        )
        self._test_create_community(
            username=str(), instance_path='event/community',
            created_under=self.community_event.id, allows_create=False
        )

    def test_create_community_event_under_lab(self):
        ''' Test create community event under event '''
        self._test_create_community(
            username='lecturer_01', instance_path='event/community', created_under=self.lab.id, allows_create=True
        )
        self._test_create_community(
            username='lecturer_02', instance_path='event/community', created_under=self.lab.id, allows_create=True
        )
        self._test_create_community(
            username='user_03', instance_path='event/community', created_under=self.lab.id, allows_create=True
        )
        self._test_create_community(
            username='user_04', instance_path='event/community', created_under=self.lab.id, allows_create=False
        )
        self._test_create_community(
            username='user_05', instance_path='event/community', created_under=self.lab.id, allows_create=False
        )
        self._test_create_community(
            username=str(), instance_path='event/community', created_under=self.lab.id, allows_create=False
        )

    def test_create_lab(self):
        ''' Test create lab '''
        self._test_create_community(username='user_05', instance_path='lab', allows_create=False)
        self._test_create_community(username='lecturer_01', instance_path='lab', allows_create=True)
        self._test_create_community(username='support', instance_path='lab', allows_create=False)
        self._test_create_community(username=str(), instance_path='lab', allows_create=False)

    def _test_create_community(self, username=str(), instance_path='club', created_under=int(), allows_create=True):
        ''' Test create community '''
        if username.strip() != str():
            self.client.login(username=username, password='12345678')

        response = self.client.post('/api/community/{}/'.format(instance_path), {
            'name_th': 'สังคมใหม่ โดย {}'.format(username),
            'name_en': 'New Community by {}'.format(username),
            'location': '-',
            'start_date': '2021-01-01',
            'end_date': '2021-01-02',
            'start_time': '08:15:00',
            'end_time': '15:45:00',
            'created_under': created_under
        })

        if allows_create:
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            self.assertEqual(
                len(Membership.objects.filter(
                    user_id=get_user_model().objects.get(username=username),
                    community_id=response.data['id'],
                    position=3,
                    status='A'
                )), 1
            )
        else:
            self.assertIn(response.status_code, (status.HTTP_400_BAD_REQUEST, status.HTTP_403_FORBIDDEN))

        if username.strip() != str():
            self.client.logout()

    def test_update_club(self):
        ''' Test update club '''
        self._test_update_community(
            username='user_01', community_id=self.club_public.id, instance_path='club', allows_update=True
        )
        self._test_update_community(
            username='user_02', community_id=self.club_public.id, instance_path='club', allows_update=True
        )
        self._test_update_community(
            username='user_03', community_id=self.club_public.id, instance_path='club', allows_update=False
        )
        self._test_update_community(
            username='user_04', community_id=self.club_public.id, instance_path='club', allows_update=False
        )
        self._test_update_community(
            username='user_05', community_id=self.club_public.id, instance_path='club', allows_update=False
        )
        self._test_update_community(
            username=str(), community_id=self.club_public.id, instance_path='club', allows_update=False
        )

    def test_update_event(self):
        ''' Test update event'''
        self._test_update_community(
            username='user_01', community_id=self.event.id, instance_path='event', allows_update=True
        )
        self._test_update_community(
            username='user_02', community_id=self.event.id, instance_path='event', allows_update=True
        )
        self._test_update_community(
            username='user_03', community_id=self.event.id, instance_path='event', allows_update=False
        )
        self._test_update_community(
            username='user_04', community_id=self.event.id, instance_path='event', allows_update=False
        )
        self._test_update_community(
            username='user_05', community_id=self.event.id, instance_path='event', allows_update=False
        )
        self._test_update_community(
            username=str(), community_id=self.event.id, instance_path='event', allows_update=False
        )

    def test_update_community_event(self):
        ''' Test update community event '''
        self._test_update_community(
            username='user_01', community_id=self.community_event.id,
            instance_path='event/community', allows_update=True
        )
        self._test_update_community(
            username='user_02', community_id=self.community_event.id,
            instance_path='event/community', allows_update=True
        )
        self._test_update_community(
            username='user_03', community_id=self.community_event.id,
            instance_path='event/community', allows_update=False
        )
        self._test_update_community(
            username='user_04', community_id=self.community_event.id,
            instance_path='event/community', allows_update=False
        )
        self._test_update_community(
            username='user_05', community_id=self.community_event.id,
            instance_path='event/community', allows_update=False
        )
        self._test_update_community(
            username=str(), community_id=self.community_event.id,
            instance_path='event/community', allows_update=False
        )

    def test_update_lab(self):
        ''' Test update lab '''
        self._test_update_community(
            username='lecturer_01', community_id=self.lab.id, instance_path='lab', allows_update=True
        )
        self._test_update_community(
            username='lecturer_02', community_id=self.lab.id, instance_path='lab', allows_update=True
        )
        self._test_update_community(
            username='user_03', community_id=self.lab.id, instance_path='lab', allows_update=False
        )
        self._test_update_community(
            username='user_04', community_id=self.lab.id, instance_path='lab', allows_update=False
        )
        self._test_update_community(
            username='user_05', community_id=self.lab.id, instance_path='lab', allows_update=False
        )
        self._test_update_community(
            username=str(), community_id=self.lab.id, instance_path='lab', allows_update=False
        )

    def _test_update_community(self, username=str(), community_id=int(), instance_path='club', allows_update=True):
        ''' Test update community '''
        if username.strip() != str():
            self.client.login(username=username, password='12345678')

        description = get_random_string(length=64)

        response = self.client.patch('/api/community/{}/{}/'.format(instance_path, community_id), {
            'description': description
        })

        if allows_update:
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(Community.objects.get(pk=community_id).description, description)
        else:
            self.assertIn(response.status_code, (status.HTTP_400_BAD_REQUEST, status.HTTP_403_FORBIDDEN))
