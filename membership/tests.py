'''
    Membership Application Tests
    generator/tests.py
    @author Teerapat Kraisrisirikul (810Teams)
'''

from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from community.models import Club, Event, Lab, CommunityEvent
from membership.models import Membership, Request, Invitation

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


class InvitationAPITest(APITestCase):
    ''' Invitation API test '''
    def setUp(self):
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

        Membership.objects.create(community_id=self.event.id, user_id=self.user_01.id, position=3)
        Membership.objects.create(community_id=self.lab.id, user_id=self.user_01.id, position=3)
        Membership.objects.create(
            community_id=self.community_event_allows_outside.id, user_id=self.user_01.id, position=3
        )
        Membership.objects.create(
            community_id=self.community_event_disallows_outside.id, user_id=self.user_01.id, position=3
        )

    def test_retrieve_invitation_as_member(self):
        ''' Test retrieve invitation as different member positions '''
        invitation = Invitation.objects.create(
            invitor_id=self.user_01.id, invitee_id=self.user_05.id, community_id=self.club.id
        )

        # Access request as leader position
        self.client.login(username='user_01', password='12345678')
        response = self.client.get('/api/membership/invitation/{}/'.format(invitation.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.client.logout()

        # Access request as deputy leader position
        self.client.login(username='user_02', password='12345678')
        response = self.client.get('/api/membership/invitation/{}/'.format(invitation.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.client.logout()

        # Access request as staff position
        self.client.login(username='user_03', password='12345678')
        response = self.client.get('/api/membership/invitation/{}/'.format(invitation.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.client.logout()

        # Access request as member position
        self.client.login(username='user_04', password='12345678')
        response = self.client.get('/api/membership/invitation/{}/'.format(invitation.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.client.logout()

    def test_retrieve_invitation_as_receiver(self):
        ''' Test retrieve invitation as receiver and non-receiver '''
        invitation = Invitation.objects.create(
            invitor_id=self.user_01.id, invitee_id=self.user_05.id, community_id=self.club.id
        )

        # Access invitation as receiver
        self.client.login(username='user_05', password='12345678')
        response = self.client.get('/api/membership/invitation/{}/'.format(invitation.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.client.logout()

        # Access invitation as someone else being both non-member and not invitation sender
        self.client.login(username='user_06', password='12345678')
        response = self.client.get('/api/membership/invitation/{}/'.format(invitation.id))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.client.logout()

    def test_send_invitation_to_non_member(self):
        ''' Test send invitation to user which is not a member '''
        self.client.login(username='user_01', password='12345678')

        response = self.client.post('/api/membership/invitation/', {
            'invitee': self.user_05.id,
            'community': self.club.id
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.client.logout()

    def test_send_invitation_to_left_member(self):
        ''' Test send invitation to user which has already left the community '''
        self.client.login(username='user_01', password='12345678')

        Membership.objects.create(user_id=self.user_06.id, community_id=self.club.id, status='L')
        response = self.client.post('/api/membership/invitation/', {
            'invitee': self.user_06.id,
            'community': self.club.id
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.client.logout()

    def test_send_invitation_to_removed_member(self):
        ''' Test send invitation to user which has been removed from the community '''
        self.client.login(username='user_01', password='12345678')

        Membership.objects.create(user_id=self.user_07.id, community_id=self.club.id, status='X')
        response = self.client.post('/api/membership/invitation/', {
            'invitee': self.user_07.id,
            'community': self.club.id
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.client.logout()

    def test_send_invitation_to_active_member(self):
        ''' Test send invitation to user which is already a member '''
        self.client.login(username='user_01', password='12345678')

        response = self.client.post('/api/membership/invitation/', {
            'invitee': self.user_04.id,
            'community': self.club.id
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.client.logout()

    def test_send_invitation_to_retired_member(self):
        ''' Test send invitation to user which has already retired '''
        self.client.login(username='user_01', password='12345678')

        Membership.objects.create(user_id=self.user_05.id, community_id=self.club.id, status='R')
        response = self.client.post('/api/membership/invitation/', {
            'invitee': self.user_05.id,
            'community': self.club.id
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.client.logout()

    def test_send_invitation_to_non_base_member(self):
        ''' Test send invitation to non-members of base community '''
        self.client.login(username='user_01', password='12345678')

        response = self.client.post('/api/membership/invitation/', {
            'invitee': self.user_05.id,
            'community': self.community_event_allows_outside.id
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        response = self.client.post('/api/membership/invitation/', {
            'invitee': self.user_05.id,
            'community': self.community_event_disallows_outside.id
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.client.logout()

    def test_send_invitation_duplicate(self):
        ''' Test send duplicate invitation  '''
        self.client.login(username='user_01', password='12345678')

        Invitation.objects.create(invitor_id=self.user_01.id, invitee_id=self.user_05.id, community_id=self.club.id)
        response = self.client.post('/api/membership/invitation/', {
            'invitee': self.user_05.id,
            'community': self.club.id
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.client.logout()

    def test_send_invitation_to_student(self):
        ''' Test send invitation to student '''
        self._test_send_invitation_to(
            'user_05', club=True, event=True, lab=True,
            community_event_allows_outside=True, community_event_disallows_outside=False
        )

    def test_send_invitation_to_lecturer(self):
        ''' Test send invitation to lecturer '''
        self._test_send_invitation_to(
            'lecturer', club=False, event=True, lab=True,
            community_event_allows_outside=True, community_event_disallows_outside=False
        )

    def test_send_invitation_to_support(self):
        ''' Test send invitation to support staff '''
        self._test_send_invitation_to(
            'support', club=False, event=True, lab=False,
            community_event_allows_outside=True, community_event_disallows_outside=False
        )

    def _test_send_invitation_to(self, username, club=True, event=True, lab=True, community_event_allows_outside=True,
                                 community_event_disallows_outside=False):
        ''' Test send invitation to different user groups '''
        self.client.login(username='user_01', password='12345678')
        invitee = get_user_model().objects.get(username=username)

        # Invitation from club
        self.client.post('/api/membership/invitation/', {
            'invitee': invitee.id,
            'community': self.club.id
        })
        self.assertEqual(len(Invitation.objects.filter(invitee_id=invitee.id, community_id=self.club.id)), int(club))

        # Invitation from event
        self.client.post('/api/membership/invitation/', {
            'invitee': invitee.id,
            'community': self.event.id
        })
        self.assertEqual(len(Invitation.objects.filter(invitee_id=invitee.id, community_id=self.event.id)), int(event))

        # Invitation from lab
        self.client.post('/api/membership/invitation/', {
            'invitee': invitee.id,
            'community': self.lab.id
        })
        self.assertEqual(len(Invitation.objects.filter(invitee_id=invitee.id, community_id=self.lab.id)), int(lab))

        # Invitation from community event that allows outside participators
        self.client.post('/api/membership/invitation/', {
            'invitee': invitee.id,
            'community': self.community_event_allows_outside.id
        })
        self.assertEqual(
            len(Invitation.objects.filter(invitee_id=invitee.id, community_id=self.community_event_allows_outside.id)),
            int(community_event_allows_outside)
        )

        # Invitation from community event that does not allow outside participators
        self.client.post('/api/membership/invitation/', {
            'invitee': invitee.id,
            'community': self.community_event_disallows_outside.id
        })
        self.assertEqual(
            len(Invitation.objects.filter(
                invitee_id=invitee.id, community_id=self.community_event_disallows_outside.id)
            ),
            int(community_event_disallows_outside)
        )

        self.client.logout()

    def test_send_invitation_as_leader(self):
        ''' Test send invitation as leader '''
        self._test_send_invitation_as('user_01', allows_sending=True)

    def test_send_invitation_as_deputy_leader(self):
        ''' Test send invitation as leader '''
        self._test_send_invitation_as('user_02', allows_sending=True)

    def test_send_invitation_as_staff(self):
        ''' Test send invitation as leader '''
        self._test_send_invitation_as('user_03', allows_sending=True)

    def test_send_invitation_as_member(self):
        ''' Test send invitation as leader '''
        self._test_send_invitation_as('user_04', allows_sending=False)

    def test_send_invitation_as_non_member(self):
        ''' Test send invitation as leader '''
        self._test_send_invitation_as('user_05', allows_sending=False)

    def _test_send_invitation_as(self, username, allows_sending=True):
        ''' Test send invitation as different membership positions '''
        self.client.login(username=username, password='12345678')

        response = self.client.post('/api/membership/invitation/', {
            'invitee': self.user_06.id,
            'community': self.club.id
        })

        if allows_sending:
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            self.assertEqual(len(Invitation.objects.filter(invitee_id=self.user_06.id, community_id=self.club.id)), 1)
        else:
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertEqual(len(Invitation.objects.filter(invitee_id=self.user_06.id, community_id=self.club.id)), 0)

        self.client.logout()

    def test_accept_invitation_own(self):
        ''' Test accept own invitation '''
        self.client.login(username='user_05', password='12345678')

        invitation = Invitation.objects.create(
            invitor_id=self.user_01.id, invitee_id=self.user_05.id, community_id=self.club.id
        )
        response = self.client.patch('/api/membership/invitation/{}/'.format(invitation.id), {
            'status': 'A'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Invitation.objects.get(id=invitation.id).status, 'A')
        self.assertEqual(len(Membership.objects.filter(user_id=self.user_05.id, community_id=self.club.id)), 1)

        self.client.logout()

    def test_decline_invitation_own(self):
        ''' Test decline own invitation '''
        self.client.login(username='user_05', password='12345678')

        invitation = Invitation.objects.create(
            invitor_id=self.user_01.id, invitee_id=self.user_05.id, community_id=self.club.id
        )
        response = self.client.patch('/api/membership/invitation/{}/'.format(invitation.id), {
            'status': 'D'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(Membership.objects.filter(user_id=self.user_05.id, community_id=self.club.id)), 0)

        self.client.logout()

    def test_accept_invitation_other(self):
        ''' Test accept own invitation '''
        self.client.login(username='user_05', password='12345678')

        invitation = Invitation.objects.create(
            invitor_id=self.user_01.id, invitee_id=self.user_06.id, community_id=self.club.id
        )
        response = self.client.patch('/api/membership/invitation/{}/'.format(invitation.id), {
            'status': 'A'
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(len(Membership.objects.filter(user_id=self.user_05.id, community_id=self.club.id)), 0)

        self.client.logout()

    def test_decline_invitation_other(self):
        ''' Test decline own invitation '''
        self.client.login(username='user_05', password='12345678')

        invitation = Invitation.objects.create(
            invitor_id=self.user_01.id, invitee_id=self.user_06.id, community_id=self.club.id
        )
        response = self.client.patch('/api/membership/invitation/{}/'.format(invitation.id), {
            'status': 'D'
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(len(Membership.objects.filter(user_id=self.user_05.id, community_id=self.club.id)), 0)

        self.client.logout()

    def test_respond_invitation_already_accepted(self):
        ''' Test respond to invitation that is already accepted '''
        self.client.login(username='user_05', password='12345678')

        invitation = Invitation.objects.create(invitee_id=self.user_05.id, community_id=self.club.id, status='A')
        response = self.client.patch('/api/membership/invitation/{}/'.format(invitation.id), {
            'status': 'W'
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Invitation.objects.get(pk=invitation.id).status, 'A')

        response = self.client.patch('/api/membership/invitation/{}/'.format(invitation.id), {
            'status': 'A'
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Invitation.objects.get(pk=invitation.id).status, 'A')

        response = self.client.patch('/api/membership/invitation/{}/'.format(invitation.id), {
            'status': 'D'
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Invitation.objects.get(pk=invitation.id).status, 'A')

        self.client.logout()

    def test_respond_invitation_already_declined(self):
        ''' Test respond to invitation that is already accepted '''
        self.client.login(username='user_05', password='12345678')

        invitation = Invitation.objects.create(invitee_id=self.user_05.id, community_id=self.club.id, status='D')
        response = self.client.patch('/api/membership/invitation/{}/'.format(invitation.id), {
            'status': 'W'
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Invitation.objects.get(pk=invitation.id).status, 'D')

        response = self.client.patch('/api/membership/invitation/{}/'.format(invitation.id), {
            'status': 'A'
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Invitation.objects.get(pk=invitation.id).status, 'D')

        response = self.client.patch('/api/membership/invitation/{}/'.format(invitation.id), {
            'status': 'D'
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Invitation.objects.get(pk=invitation.id).status, 'D')

        self.client.logout()

    def test_respond_invitation_renew_membership(self):
        ''' Test respond to invitation that renews membership '''
        self.client.login(username='user_05', password='12345678')

        membership = Membership.objects.create(user_id=self.user_05.id, community_id=self.club.id, status='L')
        invitation = Invitation.objects.create(invitee_id=self.user_05.id, community_id=self.club.id)
        response = self.client.patch('/api/membership/invitation/{}/'.format(invitation.id), {
            'status': 'A'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Membership.objects.get(pk=membership.id).status, 'A')
        self.assertEqual(len(Membership.objects.filter(user_id=self.user_05.id, community_id=self.club.id)), 1)

        self.client.logout()

    def test_cancel_own_invitation(self):
        ''' Test cancel own invitation '''
        self.client.login(username='user_03', password='12345678')

        invitation = Invitation.objects.create(
            invitor_id=self.user_03.id, invitee_id=self.user_06.id, community_id=self.club.id
        )
        response = self.client.delete('/api/membership/invitation/{}/'.format(invitation.id))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(len(Invitation.objects.filter(invitee_id=self.user_06.id, community_id=self.club.id)), 0)

        self.client.logout()

    def test_cancel_invitation_as_leader(self):
        ''' Test cancel invitation as leader '''
        self._test_cancel_invitation_as('user_01', allows_cancel=True)

    def test_cancel_invitation_as_deputy_leader(self):
        ''' Test cancel invitation as deputy leader '''
        self._test_cancel_invitation_as('user_02', allows_cancel=True)

    def test_cancel_invitation_as_staff(self):
        ''' Test cancel invitation as staff '''
        self._test_cancel_invitation_as('user_03', allows_cancel=False)

    def test_cancel_invitation_as_member(self):
        ''' Test cancel invitation as member '''
        self._test_cancel_invitation_as('user_04', allows_cancel=False)

    def test_cancel_invitation_as_non_member(self):
        ''' Test cancel invitation as leader '''
        self._test_cancel_invitation_as('user_05', allows_cancel=False)

    def _test_cancel_invitation_as(self, username, allows_cancel=True):
        ''' Test cancel invitation as different membership positions '''
        self.client.login(username=username, password='12345678')

        invitation = Invitation.objects.create(
            invitor_id=None, invitee_id=self.user_06.id, community_id=self.club.id
        )
        response = self.client.delete('/api/membership/invitation/{}/'.format(invitation.id))

        if allows_cancel:
            self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
            self.assertEqual(len(Invitation.objects.filter(invitee_id=self.user_06.id, community_id=self.club.id)), 0)
        else:
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
            self.assertEqual(len(Invitation.objects.filter(invitee_id=self.user_06.id, community_id=self.club.id)), 1)

        self.client.logout()


class MembershipAPITest(APITestCase):
    ''' Membership API test '''
    def setUp(self):
        ''' Set up '''
        self.user_01 = get_user_model().objects.create_user(username='user_01', password='12345678', name='User One')
        self.user_02 = get_user_model().objects.create_user(username='user_02', password='12345678', name='User Two')
        self.user_03 = get_user_model().objects.create_user(username='user_03', password='12345678', name='User Three')
        self.user_04 = get_user_model().objects.create_user(username='user_04', password='12345678', name='User Four')
        self.user_05 = get_user_model().objects.create_user(username='user_05', password='12345678', name='User Five')
        self.club_public = Club.objects.create(
            name_th='ชุมนุมทดสอบสมาชิก สาธารณะ', name_en='Membership Testing Club (Public)', is_publicly_visible=True
        )
        self.club_private = Club.objects.create(
            name_th='ชุมนุมทดสอบสมาชิก ส่วนตัว', name_en='Membership Testing Club (Private)'
        )

        self.m1pub = Membership.objects.create(community_id=self.club_public.id, user_id=self.user_01.id, position=3)
        self.m2pub = Membership.objects.create(community_id=self.club_public.id, user_id=self.user_02.id, position=2)
        self.m3pub = Membership.objects.create(community_id=self.club_public.id, user_id=self.user_03.id, position=1)
        self.m4pub = Membership.objects.create(community_id=self.club_public.id, user_id=self.user_04.id, position=0)

        self.m1pri = Membership.objects.create(community_id=self.club_private.id, user_id=self.user_01.id, position=3)
        self.m2pri = Membership.objects.create(community_id=self.club_private.id, user_id=self.user_02.id, position=2)
        self.m3pri = Membership.objects.create(community_id=self.club_private.id, user_id=self.user_03.id, position=1)
        self.m4pri = Membership.objects.create(community_id=self.club_private.id, user_id=self.user_04.id, position=0)

        self.memberships_public = 4
        self.memberships_private = 4

    def test_list_membership_public_authenticated(self):
        ''' Test list memberships in publicly visible community while authenticated '''
        self.client.login(username='user_05', password='12345678')

        response = self.client.get('/api/membership/membership/')
        self.assertEqual(len(response.data), self.memberships_public + self.memberships_private)

        self.client.logout()

    def test_list_membership_public_unauthenticated(self):
        ''' Test list memberships in publicly visible community while not authenticated '''
        response = self.client.get('/api/membership/membership/')
        self.assertEqual(len(response.data), self.memberships_public)

    def test_retrieve_membership_public_authenticated(self):
        ''' Test retrieve membership in publicly visible community while authenticated '''
        self.client.login(username='user_05', password='12345678')

        response = self.client.get('/api/membership/membership/{}/'.format(self.m1pub.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.get('/api/membership/membership/{}/'.format(self.m1pri.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.client.logout()

    def test_retrieve_membership_public_unauthenticated(self):
        ''' Test retrieve membership in publicly visible community while not authenticated '''
        response = self.client.get('/api/membership/membership/{}/'.format(self.m1pub.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.get('/api/membership/membership/{}/'.format(self.m1pri.id))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_membership(self):
        ''' Test create membership '''
        self.client.login(username='user_01', password='12345678')

        response = self.client.post('/api/membership/membership/', {})
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        self.client.logout()

    def test_update_membership_position_as_leader(self):
        ''' Test update membership as leader '''
        self.client.login(username='user_01', password='12345678')

        self._test_update_membership_position(self.m1pub, 0, allows_update=False)
        self._test_update_membership_position(self.m1pub, 1, allows_update=False)
        self._test_update_membership_position(self.m1pub, 2, allows_update=False)

        self._test_update_membership_position(self.m2pub, 2, allows_update=False)
        self._test_update_membership_position(self.m2pub, 0, allows_update=True)
        self._test_update_membership_position(self.m2pub, 1, allows_update=True)
        self._test_update_membership_position(self.m2pub, 2, allows_update=True)

        self._test_update_membership_position(self.m3pub, 1, allows_update=False)
        self._test_update_membership_position(self.m3pub, 0, allows_update=True)
        self._test_update_membership_position(self.m3pub, 1, allows_update=True)
        self._test_update_membership_position(self.m3pub, 2, allows_update=True)

        self._test_update_membership_position(self.m4pub, 0, allows_update=False)
        self._test_update_membership_position(self.m4pub, 1, allows_update=True)
        self._test_update_membership_position(self.m4pub, 0, allows_update=True)
        self._test_update_membership_position(self.m4pub, 2, allows_update=True)

        self.client.logout()

    def test_update_membership_position_as_deputy_leader(self):
        ''' Test update membership as deputy leader '''
        self.client.login(username='user_02', password='12345678')

        self._test_update_membership_position(self.m1pub, 0, allows_update=False)
        self._test_update_membership_position(self.m1pub, 1, allows_update=False)
        self._test_update_membership_position(self.m1pub, 2, allows_update=False)

        self._test_update_membership_position(self.m2pub, 2, allows_update=False)
        self._test_update_membership_position(self.m2pub, 0, allows_update=False)
        self._test_update_membership_position(self.m2pub, 1, allows_update=False)
        self._test_update_membership_position(self.m2pub, 2, allows_update=False)

        self._test_update_membership_position(self.m3pub, 1, allows_update=False)
        self._test_update_membership_position(self.m3pub, 0, allows_update=True)
        self._test_update_membership_position(self.m3pub, 1, allows_update=True)
        self._test_update_membership_position(self.m3pub, 2, allows_update=False)

        self._test_update_membership_position(self.m4pub, 0, allows_update=False)
        self._test_update_membership_position(self.m4pub, 1, allows_update=True)
        self._test_update_membership_position(self.m4pub, 0, allows_update=True)
        self._test_update_membership_position(self.m4pub, 2, allows_update=False)

        self.client.logout()

    def test_update_membership_position_as_staff(self):
        ''' Test update membership as staff '''
        self.client.login(username='user_03', password='12345678')

        self._test_update_membership_position(self.m1pub, 0, allows_update=False)
        self._test_update_membership_position(self.m1pub, 1, allows_update=False)
        self._test_update_membership_position(self.m1pub, 2, allows_update=False)

        self._test_update_membership_position(self.m2pub, 2, allows_update=False)
        self._test_update_membership_position(self.m2pub, 0, allows_update=False)
        self._test_update_membership_position(self.m2pub, 1, allows_update=False)
        self._test_update_membership_position(self.m2pub, 2, allows_update=False)

        self._test_update_membership_position(self.m3pub, 1, allows_update=False)
        self._test_update_membership_position(self.m3pub, 0, allows_update=False)
        self._test_update_membership_position(self.m3pub, 1, allows_update=False)
        self._test_update_membership_position(self.m3pub, 2, allows_update=False)

        self._test_update_membership_position(self.m4pub, 0, allows_update=False)
        self._test_update_membership_position(self.m4pub, 1, allows_update=False)
        self._test_update_membership_position(self.m4pub, 0, allows_update=False)
        self._test_update_membership_position(self.m4pub, 2, allows_update=False)

        self.client.logout()

    def test_update_membership_position_as_member(self):
        ''' Test update membership as member '''
        self.client.login(username='user_04', password='12345678')

        self._test_update_membership_position(self.m1pub, 0, allows_update=False)
        self._test_update_membership_position(self.m1pub, 1, allows_update=False)
        self._test_update_membership_position(self.m1pub, 2, allows_update=False)

        self._test_update_membership_position(self.m2pub, 2, allows_update=False)
        self._test_update_membership_position(self.m2pub, 0, allows_update=False)
        self._test_update_membership_position(self.m2pub, 1, allows_update=False)
        self._test_update_membership_position(self.m2pub, 2, allows_update=False)

        self._test_update_membership_position(self.m3pub, 1, allows_update=False)
        self._test_update_membership_position(self.m3pub, 0, allows_update=False)
        self._test_update_membership_position(self.m3pub, 1, allows_update=False)
        self._test_update_membership_position(self.m3pub, 2, allows_update=False)

        self._test_update_membership_position(self.m4pub, 0, allows_update=False)
        self._test_update_membership_position(self.m4pub, 1, allows_update=False)
        self._test_update_membership_position(self.m4pub, 0, allows_update=False)
        self._test_update_membership_position(self.m4pub, 2, allows_update=False)

        self.client.logout()

    def test_update_membership_position_as_non_member(self):
        ''' Test update membership as non-member '''
        self.client.login(username='user_05', password='12345678')

        self._test_update_membership_position(self.m1pub, 0, allows_update=False)
        self._test_update_membership_position(self.m1pub, 1, allows_update=False)
        self._test_update_membership_position(self.m1pub, 2, allows_update=False)

        self._test_update_membership_position(self.m2pub, 2, allows_update=False)
        self._test_update_membership_position(self.m2pub, 0, allows_update=False)
        self._test_update_membership_position(self.m2pub, 1, allows_update=False)
        self._test_update_membership_position(self.m2pub, 2, allows_update=False)

        self._test_update_membership_position(self.m3pub, 1, allows_update=False)
        self._test_update_membership_position(self.m3pub, 0, allows_update=False)
        self._test_update_membership_position(self.m3pub, 1, allows_update=False)
        self._test_update_membership_position(self.m3pub, 2, allows_update=False)

        self._test_update_membership_position(self.m4pub, 0, allows_update=False)
        self._test_update_membership_position(self.m4pub, 1, allows_update=False)
        self._test_update_membership_position(self.m4pub, 0, allows_update=False)
        self._test_update_membership_position(self.m4pub, 2, allows_update=False)

        self.client.logout()

    def _test_update_membership_position(self, membership, position, allows_update=True):
        ''' Test update membership position to different membership positions '''
        response = self.client.patch('/api/membership/membership/{}/'.format(membership.id), {
            'position': position
        })

        if allows_update:
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(Membership.objects.get(pk=membership.id).position, position)
        else:
            self.assertIn(response.status_code, (status.HTTP_400_BAD_REQUEST, status.HTTP_403_FORBIDDEN))

    def test_transfer_leader_position_to_deputy_leader(self):
        ''' Test transfer leader position to deputy leader '''
        self._test_transfer_leader_position_to(self.m2pub)

    def test_transfer_leader_position_to_staff(self):
        ''' Test transfer leader position to staff '''
        self._test_transfer_leader_position_to(self.m3pub)

    def test_transfer_leader_position_to_member(self):
        ''' Test transfer leader position to member '''
        self._test_transfer_leader_position_to(self.m4pub)

    def _test_transfer_leader_position_to(self, membership):
        ''' Test transfer leader position to different membership positions '''
        self.client.login(username='user_01', password='12345678')

        response = self.client.patch('/api/membership/membership/{}/'.format(membership.id), {
            'position': 3
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Membership.objects.get(pk=membership.id).position, 3)
        self.assertEqual(Membership.objects.get(pk=self.m1pub.id).position, 2)

        self.client.logout()

    def test_retire_as_leader(self):
        ''' Test retire as leader '''
        username = 'user_01'
        self._test_retire(username, self.m1pub, allows_update=False)
        self._test_retire(username, self.m2pub, allows_update=False)
        self._test_retire(username, self.m3pub, allows_update=False)
        self._test_retire(username, self.m4pub, allows_update=False)

    def test_retire_as_deputy_leader(self):
        ''' Test retire as deputy leader '''
        username = 'user_02'
        self._test_retire(username, self.m1pub, allows_update=False)
        self._test_retire(username, self.m2pub, allows_update=True)
        self._test_retire(username, self.m3pub, allows_update=False)
        self._test_retire(username, self.m4pub, allows_update=False)

    def test_retire_as_staff(self):
        ''' Test retire as staff '''
        username = 'user_03'
        self._test_retire(username, self.m1pub, allows_update=False)
        self._test_retire(username, self.m2pub, allows_update=False)
        self._test_retire(username, self.m3pub, allows_update=True)
        self._test_retire(username, self.m4pub, allows_update=False)

    def test_retire_as_member(self):
        ''' Test retire as member '''
        username = 'user_04'
        self._test_retire(username, self.m1pub, allows_update=False)
        self._test_retire(username, self.m2pub, allows_update=False)
        self._test_retire(username, self.m3pub, allows_update=False)
        self._test_retire(username, self.m4pub, allows_update=True)

    def test_retire_as_non_member(self):
        ''' Test retire as non_member '''
        username = 'user_05'
        self._test_retire(username, self.m1pub, allows_update=False)
        self._test_retire(username, self.m2pub, allows_update=False)
        self._test_retire(username, self.m3pub, allows_update=False)
        self._test_retire(username, self.m4pub, allows_update=False)

    def _test_retire(self, username, membership, allows_update=True):
        ''' Test retire as different membership positions '''
        self.client.login(username=username, password='12345678')

        # Test retire
        response = self.client.patch('/api/membership/membership/{}/'.format(membership.id), {
            'status': 'R'
        })
        if allows_update:
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(Membership.objects.get(pk=membership.id).status, 'R')
            self.assertEqual(Membership.objects.get(pk=membership.id).position, 0)
        else:
            self.assertIn(response.status_code, (status.HTTP_400_BAD_REQUEST, status.HTTP_403_FORBIDDEN))

        # Test duplicate retire (no update)
        response = self.client.patch('/api/membership/membership/{}/'.format(membership.id), {
            'status': 'R'
        })
        self.assertIn(response.status_code, (status.HTTP_400_BAD_REQUEST, status.HTTP_403_FORBIDDEN))

        # Test back in duty
        response = self.client.patch('/api/membership/membership/{}/'.format(membership.id), {
            'status': 'A'
        })
        if allows_update:
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(Membership.objects.get(pk=membership.id).status, 'A')
            self.assertEqual(Membership.objects.get(pk=membership.id).position, 0)
        else:
            self.assertIn(response.status_code, (status.HTTP_400_BAD_REQUEST, status.HTTP_403_FORBIDDEN))

        # Test duplicate back in duty (no update)
        response = self.client.patch('/api/membership/membership/{}/'.format(membership.id), {
            'status': 'A'
        })
        self.assertIn(response.status_code, (status.HTTP_400_BAD_REQUEST, status.HTTP_403_FORBIDDEN))

        self.client.logout()

    def test_leave_as_leader(self):
        ''' Test leave as leader '''
        username = 'user_01'
        self._test_leave_as(username, self.m1pub, allows_update=False)
        self._test_leave_as(username, self.m2pub, allows_update=False)
        self._test_leave_as(username, self.m3pub, allows_update=False)
        self._test_leave_as(username, self.m4pub, allows_update=False)

    def test_leave_as_deputy_leader(self):
        ''' Test leave as deputy leader '''
        username = 'user_02'
        self._test_leave_as(username, self.m1pub, allows_update=False)
        self._test_leave_as(username, self.m2pub, allows_update=True)
        self._test_leave_as(username, self.m3pub, allows_update=False)
        self._test_leave_as(username, self.m4pub, allows_update=False)

    def test_leave_as_staff(self):
        ''' Test leave as staff '''
        username = 'user_03'
        self._test_leave_as(username, self.m1pub, allows_update=False)
        self._test_leave_as(username, self.m2pub, allows_update=False)
        self._test_leave_as(username, self.m3pub, allows_update=True)
        self._test_leave_as(username, self.m4pub, allows_update=False)

    def test_leave_as_member(self):
        ''' Test leave as member '''
        username = 'user_04'
        self._test_leave_as(username, self.m1pub, allows_update=False)
        self._test_leave_as(username, self.m2pub, allows_update=False)
        self._test_leave_as(username, self.m3pub, allows_update=False)
        self._test_leave_as(username, self.m4pub, allows_update=True)

    def test_leave_as_non_member(self):
        ''' Test leave as non-member '''
        username = 'user_05'
        self._test_leave_as(username, self.m1pub, allows_update=False)
        self._test_leave_as(username, self.m2pub, allows_update=False)
        self._test_leave_as(username, self.m3pub, allows_update=False)
        self._test_leave_as(username, self.m4pub, allows_update=False)

    def _test_leave_as(self, username, membership, allows_update=True):
        ''' Test leave as different membership positions '''
        self.client.login(username=username, password='12345678')

        # Test leave
        response = self.client.patch('/api/membership/membership/{}/'.format(membership.id), {
            'status': 'L'
        })
        if allows_update:
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(Membership.objects.get(pk=membership.id).status, 'L')
        else:
            self.assertIn(response.status_code, (status.HTTP_400_BAD_REQUEST, status.HTTP_403_FORBIDDEN))

        # Test duplicate leave (no update)
        response = self.client.patch('/api/membership/membership/{}/'.format(membership.id), {
            'status': 'L'
        })
        self.assertIn(response.status_code, (status.HTTP_400_BAD_REQUEST, status.HTTP_403_FORBIDDEN))

        # Test illegal return
        response = self.client.patch('/api/membership/membership/{}/'.format(membership.id), {
            'status': 'A'
        })
        self.assertIn(response.status_code, (status.HTTP_400_BAD_REQUEST, status.HTTP_403_FORBIDDEN))

        # Test illegal retire
        response = self.client.patch('/api/membership/membership/{}/'.format(membership.id), {
            'status': 'R'
        })
        self.assertIn(response.status_code, (status.HTTP_400_BAD_REQUEST, status.HTTP_403_FORBIDDEN))

        self.client.logout()

    def test_delete_membership(self):
        ''' Test delete membership '''
        self.client.login(username='user_01', password='12345678')

        response = self.client.delete('/api/membership/membership/{}/'.format(self.m1pub.id))
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.delete('/api/membership/membership/{}/'.format(self.m2pub.id))
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.delete('/api/membership/membership/{}/'.format(self.m3pub.id))
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.delete('/api/membership/membership/{}/'.format(self.m4pub.id))
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        self.client.logout()
