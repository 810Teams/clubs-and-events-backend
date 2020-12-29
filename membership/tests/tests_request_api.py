'''
    Membership Application's Request API Test
    membership/tests/tests_request_api.py
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
            name_th='กิจกรรมชุมนุมทดสอบคำขอเข้าร่วม อนุญาตบุคคลภายนอก',
            name_en='Request Testing Club Event (Allows Outsiders)',
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
            name_th='กิจกรรมชุมนุมทดสอบคำขอเข้าร่วม ไม่อนุญาตบุคคลภายนอก',
            name_en='Request Testing Club Event (Disallows Outsiders)',
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

    def test_retrieve_request_as_member(self):
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

    def test_retrieve_request_as_sender(self):
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

    def test_send_request_as_non_member(self):
        ''' Test send request from user which is not a member '''
        self.client.login(username='user_05', password='12345678')

        response = self.client.post('/api/membership/request/', {
            'community': self.club.id
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.client.logout()

    def test_send_request_as_left_member(self):
        ''' Test send request from user which has already left the community '''
        self.client.login(username='user_05', password='12345678')

        Membership.objects.create(user_id=self.user_05.id, community_id=self.club.id, status='L')
        response = self.client.post('/api/membership/request/', {
            'community': self.club.id
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.client.logout()

    def test_send_request_as_removed_member(self):
        ''' Test send request from user which has been removed from the community '''
        self.client.login(username='user_05', password='12345678')

        Membership.objects.create(user_id=self.user_05.id, community_id=self.club.id, status='X')
        response = self.client.post('/api/membership/request/', {
            'community': self.club.id
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.client.logout()

    def test_send_request_as_active_member(self):
        ''' Test send request from user which is already a member '''
        self.client.login(username='user_01', password='12345678')

        response = self.client.post('/api/membership/request/', {
            'community': self.club.id
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.client.logout()

    def test_send_request_as_retired_member(self):
        ''' Test send request from user which is a retired member '''
        self.client.login(username='user_05', password='12345678')

        Membership.objects.create(user_id=self.user_05.id, community_id=self.club.id, status='R')
        response = self.client.post('/api/membership/request/', {
            'community': self.club.id
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.client.logout()

    def test_send_request_as_base_member(self):
        ''' Test send request to a community event as a member of base community '''
        self.client.login(username='user_04', password='12345678')

        response = self.client.post('/api/membership/request/', {
            'community': self.community_event_allows_outside.id
        })
        self.assertEqual(response.data['status'], 'A')
        self.assertEqual(
            len(Membership.objects.filter(
                user_id=self.user_04.id, community_id=self.community_event_allows_outside.id
            )),
            1
        )

        response = self.client.post('/api/membership/request/', {
            'community': self.community_event_disallows_outside.id
        })
        self.assertEqual(response.data['status'], 'A')
        self.assertEqual(
            len(Membership.objects.filter(
                user_id=self.user_04.id, community_id=self.community_event_disallows_outside.id
            )),
            1
        )

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

    def test_send_request_to_not_accepting_request_community(self):
        ''' Test send request to a community which does not accept requests '''
        self.client.login(username='user_05', password='12345678')

        club = Club.objects.create(
            name_th='ชุมนุมไม่รับคำขอเข้าร่วม', name_en='Not Accepting Requests Club', is_accepting_requests=False
        )
        response = self.client.post('/api/membership/request/', {
            'community': club.id
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.client.logout()

    def test_send_request_as_student(self):
        ''' Test send requests as student '''
        self._test_send_request_as(
            'user_05', club=True, event=True, lab=True,
            community_event_allows_outside=True, community_event_disallows_outside=False
        )

    def test_send_request_as_lecturer(self):
        ''' Test send requests as lecturer '''
        self._test_send_request_as(
            'lecturer', club=False, event=True, lab=True,
            community_event_allows_outside=True, community_event_disallows_outside=False
        )

    def test_send_request_as_support(self):
        ''' Test send requests as support staff '''
        self._test_send_request_as(
            'support', club=False, event=True, lab=False,
            community_event_allows_outside=True, community_event_disallows_outside=False
        )

    def _test_send_request_as(self, username, club=True, event=True, lab=True, community_event_allows_outside=True,
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

    def test_respond_request_already_accepted(self):
        ''' Test respond to request that is already accepted '''
        self.client.login(username='user_01', password='12345678')

        request = Request.objects.create(user_id=self.user_05.id, community_id=self.club.id, status='A')
        response = self.client.patch('/api/membership/request/{}/'.format(request.id), {
            'status': 'W'
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Request.objects.get(pk=request.id).status, 'A')

        response = self.client.patch('/api/membership/request/{}/'.format(request.id), {
            'status': 'A'
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Request.objects.get(pk=request.id).status, 'A')

        response = self.client.patch('/api/membership/request/{}/'.format(request.id), {
            'status': 'D'
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Request.objects.get(pk=request.id).status, 'A')

        self.client.logout()

    def test_respond_request_already_declined(self):
        ''' Test respond to request that is already accepted '''
        self.client.login(username='user_01', password='12345678')

        request = Request.objects.create(user_id=self.user_05.id, community_id=self.club.id, status='D')
        response = self.client.patch('/api/membership/request/{}/'.format(request.id), {
            'status': 'W'
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Request.objects.get(pk=request.id).status, 'D')

        response = self.client.patch('/api/membership/request/{}/'.format(request.id), {
            'status': 'A'
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Request.objects.get(pk=request.id).status, 'D')

        response = self.client.patch('/api/membership/request/{}/'.format(request.id), {
            'status': 'D'
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Request.objects.get(pk=request.id).status, 'D')

        self.client.logout()

    def test_respond_request_renew_membership(self):
        ''' Test respond request that renews membership '''
        self.client.login(username='user_01', password='12345678')

        membership = Membership.objects.create(user_id=self.user_05.id, community_id=self.club.id, status='L')
        request = Request.objects.create(user_id=self.user_05.id, community_id=self.club.id)
        response = self.client.patch('/api/membership/request/{}/'.format(request.id), {
            'status': 'A'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Membership.objects.get(pk=membership.id).status, 'A')
        self.assertEqual(len(Membership.objects.filter(user_id=self.user_05.id, community_id=self.club.id)), 1)

        self.client.logout()

    def test_respond_request_as_leader(self):
        ''' Test accept and decline requests as leader '''
        self._test_respond_request_as('user_01', allows_update=True)

    def test_respond_request_as_deputy_leader(self):
        ''' Test accept and decline requests as deputy leader '''
        self._test_respond_request_as('user_02', allows_update=True)

    def test_respond_request_as_staff(self):
        ''' Test accept and decline requests as staff '''
        self._test_respond_request_as('user_03', allows_update=True)

    def test_respond_request_as_member(self):
        ''' Test accept and decline requests as member '''
        self._test_respond_request_as('user_04', allows_update=False)

    def test_respond_request_as_non_member(self):
        ''' Test accept and decline requests as non-member '''
        self._test_respond_request_as('user_05', allows_update=False)

    def _test_respond_request_as(self, username, allows_update=True):
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
        ''' Test cancel other user's request '''
        self.client.login(username='user_01', password='12345678')

        request = Request.objects.create(user_id=self.user_05.id, community_id=self.club.id)
        response = self.client.delete('/api/membership/request/{}/'.format(request.id))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(len(Request.objects.filter(id=request.id)), 1)

        self.client.logout()
