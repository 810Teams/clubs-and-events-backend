'''
    Membership Application's Invitation API Test
    membership/tests/invitation_api_test.py
    @author Teerapat Kraisrisirikul (810Teams)
'''

from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from community.models import Club, Event, Lab, CommunityEvent
from membership.models import Membership, Invitation

import datetime


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
        