'''
    Membership Application Tests
    generator/tests.py
    @author Teerapat Kraisrisirikul (810Teams)
'''

from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from community.models import Club, Event, Lab, CommunityEvent
from membership.models import Membership, Request

import datetime


class RequestAPITest(APITestCase):
    ''' Request API test '''
    def setUp(self):
        ''' Set up '''
        self.user_01 = get_user_model().objects.create_user(username='user_01', password='12345678', name='User One')
        self.user_02 = get_user_model().objects.create_user(username='user_02', password='12345678', name='User Two')
        self.user_03 = get_user_model().objects.create_user(username='user_03', password='12345678', name='User Three')
        self.user_04 = get_user_model().objects.create_user(username='user_04', password='12345678', name='User Four')
        self.user_05 = get_user_model().objects.create_user(username='user_05', password='12345678', name='User Five')
        self.user_06 = get_user_model().objects.create_user(username='user_06', password='12345678', name='User Six')
        self.user_07 = get_user_model().objects.create_user(username='user_07', password='12345678', name='User Seven')
        self.lecturer = get_user_model().objects.create_user(
            username='lecturer', password='12345678', name='Prof.Lazy Bones', user_group='lecturer'
        )
        self.support_staff = get_user_model().objects.create_user(
            username='support', password='12345678', name='Mr.Supporter', user_group='support'
        )
        self.club = Club.objects.create(name_th='ชุมนุมทดสอบคำขอเข้าร่วม', name_en='Request Testing Club')
        self.event = Event.objects.create(
            name_th='กิจกรรมทดสอบคำขอเข้าร่วม',
            name_en='Request Testing Event',
            is_approved=True,
            location='L207 IT KMITL',
            start_date=datetime.date(2020, 12, 1),
            end_date=datetime.date(2020, 12, 2),
            start_time=datetime.time(9, 0, 0),
            end_time=datetime.time(17, 0, 0)
        )
        self.lab = Lab.objects.create(name_th='ห้องปฏิบัติการทดสอบคำขอเข้าร่วม', name_en='Request Testing Lab')
        self.community_event_allows_outside = CommunityEvent.objects.create(
            name_th='กิจกรรมชุมนุมทดสอบคำขอเข้าร่วม',
            name_en='Request Testing Club Event',
            is_approved=True,
            location='L207 IT KMITL',
            start_date=datetime.date(2020, 12, 1),
            end_date=datetime.date(2020, 12, 2),
            start_time=datetime.time(9, 0, 0),
            end_time=datetime.time(17, 0, 0),
            created_under_id=self.club.id,
            allows_outside_participators=True
        )
        self.community_event_disallows_outside = CommunityEvent.objects.create(
            name_th='กิจกรรมห้องปฏิบัติการทดสอบคำขอเข้าร่วม',
            name_en='Request Testing Lab Event',
            is_approved=True,
            location='L207 IT KMITL',
            start_date=datetime.date(2020, 12, 1),
            end_date=datetime.date(2020, 12, 2),
            start_time=datetime.time(9, 0, 0),
            end_time=datetime.time(17, 0, 0),
            created_under_id=self.club.id,
            allows_outside_participators=False
        )

        Membership.objects.create(community_id=self.club.id, user_id=self.user_01.id, position=3)
        Membership.objects.create(community_id=self.club.id, user_id=self.user_02.id, position=2)
        Membership.objects.create(community_id=self.club.id, user_id=self.user_03.id, position=1)
        Membership.objects.create(community_id=self.club.id, user_id=self.user_04.id, position=0)

    def test_retrieve_request_member(self):
        ''' Test retrieve request as different member positions '''
        request = Request.objects.create(user_id=self.user_05.id, community_id=self.club.id)

        # Access request as leader position
        self.client.login(username='user_01', password='12345678')
        response = self.client.get('/api/membership/request/{}/'.format(request.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.client.logout()

        # Access request as deputy leader position
        self.client.login(username='user_02', password='12345678')
        response = self.client.get('/api/membership/request/{}/'.format(request.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.client.logout()

        # Access request as staff position
        self.client.login(username='user_03', password='12345678')
        response = self.client.get('/api/membership/request/{}/'.format(request.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.client.logout()

        # Access request as member position
        self.client.login(username='user_04', password='12345678')
        response = self.client.get('/api/membership/request/{}/'.format(request.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.client.logout()

    def test_retrieve_request_sender(self):
        ''' Test retrieve request as sender and non-sender '''
        request = Request.objects.create(user_id=self.user_05.id, community_id=self.club.id)

        # Access request as request sender (owner)
        self.client.login(username='user_05', password='12345678')
        response = self.client.get('/api/membership/request/{}/'.format(request.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.client.logout()

        # Access request as someone else being both non-member and not request sender
        self.client.login(username='user_06', password='12345678')
        response = self.client.get('/api/membership/request/{}/'.format(request.id))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.client.logout()

    def test_send_request_not_member(self):
        ''' Test send request from user which is not a member '''
        self.client.login(username='user_05', password='12345678')

        response = self.client.post('/api/membership/request/', {
            'community': self.club.id
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.client.logout()

    def test_send_request_already_member(self):
        ''' Test send request from user which is already a member '''
        self.client.login(username='user_01', password='12345678')

        response = self.client.post('/api/membership/request/', {
            'community': self.club.id
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.client.logout()

    def test_send_request_duplicate(self):
        ''' Test send duplicate request  '''
        self.client.login(username='user_05', password='12345678')

        Request.objects.create(user_id=self.user_05.id, community_id=self.club.id)
        response = self.client.post('/api/membership/request/', {
            'community': self.club.id
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.client.logout()

    def test_send_request_student(self):
        ''' Test send requests as student '''
        self._test_send_request(
            'user_05', club=True, event=True, lab=True,
            community_event_allows_outside=True, community_event_disallows_outside=False
        )

    def test_send_request_lecturer(self):
        ''' Test send requests as lecturer '''
        self._test_send_request(
            'lecturer', club=False, event=True, lab=True,
            community_event_allows_outside=True, community_event_disallows_outside=False
        )

    def test_send_request_support(self):
        ''' Test send requests as support staff '''
        self._test_send_request(
            'support', club=False, event=True, lab=False,
            community_event_allows_outside=True, community_event_disallows_outside=False
        )

    def _test_send_request(self, username, club=True, event=True, lab=True, community_event_allows_outside=True,
                           community_event_disallows_outside=False):
        ''' Test send requests as different user groups '''
        self.client.login(username=username, password='12345678')
        user = get_user_model().objects.get(username=username)

        # Request to club
        self.client.post('/api/membership/request/', {
            'community': self.club.id
        })
        self.assertEqual(len(Request.objects.filter(user_id=user.id, community_id=self.club.id)), int(club))

        # Request to event
        self.client.post('/api/membership/request/', {
            'community': self.event.id
        })
        self.assertEqual(len(Request.objects.filter(user_id=user.id, community_id=self.event.id)), int(event))

        # Request to lab
        self.client.post('/api/membership/request/', {
            'community': self.lab.id
        })
        self.assertEqual(len(Request.objects.filter(user_id=user.id, community_id=self.lab.id)), int(lab))

        # Request to community event that allows outside participators
        self.client.post('/api/membership/request/', {
            'community': self.community_event_allows_outside.id
        })
        self.assertEqual(
            len(Request.objects.filter(user_id=user.id, community_id=self.community_event_allows_outside.id)),
            int(community_event_allows_outside)
        )

        # Request to community event that does not allow outside participators
        self.client.post('/api/membership/request/', {
            'community': self.community_event_disallows_outside.id
        })
        self.assertEqual(
            len(Request.objects.filter(user_id=user.id, community_id=self.community_event_disallows_outside.id)),
            int(community_event_disallows_outside)
        )

        self.client.logout()

    def test_respond_request_leader(self):
        ''' Test accept and decline requests as leader '''
        self._test_respond_request('user_01', allows_update=True)

    def test_respond_request_deputy_leader(self):
        ''' Test accept and decline requests as deputy leader '''
        self._test_respond_request('user_02', allows_update=True)

    def test_respond_request_staff(self):
        ''' Test accept and decline requests as staff '''
        self._test_respond_request('user_03', allows_update=True)

    def test_respond_request_member(self):
        ''' Test accept and decline requests as member '''
        self._test_respond_request('user_04', allows_update=False)

    def test_respond_request_non_member(self):
        ''' Test accept and decline requests as non-member '''
        self._test_respond_request('user_05', allows_update=False)

    def _test_respond_request(self, username, allows_update=True):
        ''' Test accept and decline requests with different membership positions '''
        self.client.login(username=username, password='12345678')

        # Accepting Request Test
        request = Request.objects.create(user_id=self.user_06.id, community_id=self.club.id)
        response = self.client.patch('/api/membership/request/{}/'.format(request.id), {
            'status': 'A'
        })

        if allows_update:
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(Request.objects.get(id=request.id).status, 'A')
            self.assertEqual(len(Membership.objects.filter(user_id=self.user_06.id, community_id=self.club.id)), 1)
        else:
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
            self.assertEqual(Request.objects.get(id=request.id).status, 'W')
            self.assertEqual(len(Membership.objects.filter(user_id=self.user_06.id, community_id=self.club.id)), 0)

        # Declining Request Test
        request = Request.objects.create(user_id=self.user_07.id, community_id=self.club.id)
        response = self.client.patch('/api/membership/request/{}/'.format(request.id), {
            'status': 'D'
        })

        if allows_update:
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(Request.objects.get(id=request.id).status, 'D')
            self.assertEqual(len(Membership.objects.filter(user_id=self.user_07.id, community_id=self.club.id)), 0)
        else:
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
            self.assertEqual(Request.objects.get(id=request.id).status, 'W')
            self.assertEqual(len(Membership.objects.filter(user_id=self.user_07.id, community_id=self.club.id)), 0)

        self.client.logout()

    def test_cancel_request_own(self):
        ''' Test cancel own request '''
        self.client.login(username='user_05', password='12345678')

        request = Request.objects.create(user_id=self.user_05.id, community_id=self.club.id)
        response = self.client.delete('/api/membership/request/{}/'.format(request.id))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(len(Request.objects.filter(id=request.id)), 0)

        self.client.logout()

    def test_cancel_request_other(self):
        ''' Test cancel own request '''
        self.client.login(username='user_01', password='12345678')

        request = Request.objects.create(user_id=self.user_05.id, community_id=self.club.id)
        response = self.client.delete('/api/membership/request/{}/'.format(request.id))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(len(Request.objects.filter(id=request.id)), 1)

        self.client.logout()
