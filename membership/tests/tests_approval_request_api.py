'''
    Membership Application's Approval Request API Test
    membership/tests/tests_approval_request_api.py
    @author Teerapat Kraisrisirikul (810Teams)
'''

from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from clubs_and_events.settings import CLUB_ADVANCED_RENEWAL
from community.models import Club, Event, Lab, CommunityEvent
from membership.models import Membership, ApprovalRequest
from user.models import StudentCommitteeAuthority

import datetime


class ApprovalRequestAPITest(APITestCase):
    ''' Approval request API test '''
    def setUp(self):
        ''' Set up '''
        self.user_01 = get_user_model().objects.create_user(username='user_01', password='12345678', name='User One')
        self.user_02 = get_user_model().objects.create_user(username='user_02', password='12345678', name='User Two')
        self.user_03 = get_user_model().objects.create_user(username='user_03', password='12345678', name='User Three')
        self.user_04 = get_user_model().objects.create_user(username='user_04', password='12345678', name='User Four')
        self.user_05 = get_user_model().objects.create_user(username='user_05', password='12345678', name='User Five')
        self.user_06 = get_user_model().objects.create_user(username='user_06', password='12345678', name='User Six')
        self.lecturer = get_user_model().objects.create_user(
            username='lecturer', password='12345678', name='Prof.Lazy Bones', user_group='lecturer'
        )
        self.support_staff = get_user_model().objects.create_user(
            username='support', password='12345678', name='Mr.Supporter', user_group='support'
        )
        self.club_official = Club.objects.create(
            name_th='ชุมนุมทดสอบคำขออนุมัติ สาธารณะ', name_en='Approval Request Testing Club (Official)', is_official=True
        )
        self.club_unofficial = Club.objects.create(
            name_th='ชุมนุมทดสอบคำขออนุมัติ ส่วนตัว', name_en='Approval Request Testing Club (Unofficial)', is_official=False
        )
        self.event = Event.objects.create(
            name_th='กิจกรรมทดสอบทคำขออนุมัติ',
            name_en='Advisory Testing Event',
            is_approved=False,
            location='L207 IT KMITL',
            start_date=datetime.date(2020, 12, 1),
            end_date=datetime.date(2020, 12, 2),
            start_time=datetime.time(9, 0, 0),
            end_time=datetime.time(17, 0, 0)
        )
        self.lab = Lab.objects.create(name_th='ห้องปฏิบัติการทดสอบคำขออนุมัติ', name_en='Approval Request Testing Lab')
        self.community_event = CommunityEvent.objects.create(
            name_th='กิจกรรมชุมนุมทดสอบคำขออนุมัติ',
            name_en='Approval Request Testing Club Event',
            is_approved=True,
            location='L207 IT KMITL',
            start_date=datetime.date(2020, 12, 1),
            end_date=datetime.date(2020, 12, 2),
            start_time=datetime.time(9, 0, 0),
            end_time=datetime.time(17, 0, 0),
            created_under_id=self.club_official.id
        )

        self.m1ofc = Membership.objects.create(community_id=self.club_official.id, user_id=self.user_01.id, position=3)
        self.m2ofc = Membership.objects.create(community_id=self.club_official.id, user_id=self.user_02.id, position=2)
        self.m3ofc = Membership.objects.create(community_id=self.club_official.id, user_id=self.user_03.id, position=1)
        self.m4ofc = Membership.objects.create(community_id=self.club_official.id, user_id=self.user_04.id, position=0)

        self.m1uno = Membership.objects.create(community_id=self.club_unofficial.id, user_id=self.user_01.id, position=3)
        self.m2uno = Membership.objects.create(community_id=self.club_unofficial.id, user_id=self.user_02.id, position=2)
        self.m3uno = Membership.objects.create(community_id=self.club_unofficial.id, user_id=self.user_03.id, position=1)
        self.m4uno = Membership.objects.create(community_id=self.club_unofficial.id, user_id=self.user_04.id, position=0)

        self.m1e = Membership.objects.create(community_id=self.event.id, user_id=self.user_01.id, position=3)
        self.m1l = Membership.objects.create(community_id=self.lab.id, user_id=self.user_01.id, position=3)
        self.m1ce = Membership.objects.create(community_id=self.community_event.id, user_id=self.user_01.id, position=3)

        self.student_committee_authority = StudentCommitteeAuthority.objects.create(
            user_id=self.user_06.id, start_date=datetime.date(1970, 1, 1), end_date=datetime.date(2099, 12, 31)
        )

    def test_list_approval_request_as_leader(self):
        ''' Test list approval request as leader '''
        self._test_list_approval_request_as('user_01', allows_retrieve=True)

    def test_list_approval_request_as_deputy_leader(self):
        ''' Test list approval request as deputy leader '''
        self._test_list_approval_request_as('user_02', allows_retrieve=False)

    def test_list_approval_request_as_staff(self):
        ''' Test list approval request as staff '''
        self._test_list_approval_request_as('user_03', allows_retrieve=False)

    def test_list_approval_request_as_member(self):
        ''' Test list approval request as member '''
        self._test_list_approval_request_as('user_04', allows_retrieve=False)

    def test_list_approval_request_as_non_member(self):
        ''' Test list approval request as non_member '''
        self._test_list_approval_request_as('user_05', allows_retrieve=False)

    def test_list_approval_request_as_lecturer(self):
        ''' Test list approval request as lecturer '''
        self._test_list_approval_request_as('lecturer', allows_retrieve=False)

    def test_list_approval_request_as_support(self):
        ''' Test list approval request as support staff '''
        self._test_list_approval_request_as('support', allows_retrieve=True)

    def test_list_approval_request_as_student_committee_member(self):
        ''' Test list approval request as student_committee_member '''
        self._test_list_approval_request_as('user_06', allows_retrieve=True)

    def _test_list_approval_request_as(self, username, community=None, allows_retrieve=False):
        ''' Test list approval request as different users '''
        self.client.login(username=username, password='12345678')

        if community is None:
            community = self.club_unofficial
        ApprovalRequest.objects.create(community_id=community.id)
        response = self.client.get('/api/membership/approval-request/')

        if allows_retrieve:
            self.assertEqual(len(response.data), 1)
        else:
            self.assertEqual(len(response.data), 0)

        self.client.logout()

    def test_retrieve_approval_request_as_leader(self):
        ''' Test retrieve approval request as leader '''
        self._test_retrieve_approval_request_as('user_01', allows_retrieve=True)

    def test_retrieve_approval_request_as_deputy_leader(self):
        ''' Test retrieve approval request as deputy leader '''
        self._test_retrieve_approval_request_as('user_02', allows_retrieve=False)

    def test_retrieve_approval_request_as_staff(self):
        ''' Test retrieve approval request as staff '''
        self._test_retrieve_approval_request_as('user_03', allows_retrieve=False)

    def test_retrieve_approval_request_as_member(self):
        ''' Test retrieve approval request as member '''
        self._test_retrieve_approval_request_as('user_04', allows_retrieve=False)

    def test_retrieve_approval_request_as_non_member(self):
        ''' Test retrieve approval request as non_member '''
        self._test_retrieve_approval_request_as('user_05', allows_retrieve=False)

    def test_retrieve_approval_request_as_lecturer(self):
        ''' Test retrieve approval request as lecturer '''
        self._test_retrieve_approval_request_as('lecturer', allows_retrieve=False)

    def test_retrieve_approval_request_as_support(self):
        ''' Test retrieve approval request as support staff '''
        self._test_retrieve_approval_request_as('support', allows_retrieve=True)

    def test_retrieve_approval_request_as_student_committee_member(self):
        ''' Test retrieve approval request as student_committee_member '''
        self._test_retrieve_approval_request_as('user_06', allows_retrieve=True)

    def _test_retrieve_approval_request_as(self, username, community=None, allows_retrieve=False):
        ''' Test retrieve approval request as different users '''
        self.client.login(username=username, password='12345678')

        if community is None:
            community = self.club_unofficial
        approval_request = ApprovalRequest.objects.create(community_id=community.id)
        response = self.client.get('/api/membership/approval-request/{}/'.format(approval_request.id))

        if allows_retrieve:
            self.assertEqual(response.status_code, status.HTTP_200_OK)
        else:
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.client.logout()

    def test_create_approval_request_as_leader(self):
        ''' Test create approval request as leader '''
        self._test_create_approval_request_as('user_01', allows_create=True)

    def test_create_approval_request_as_deputy_leader(self):
        ''' Test create approval request as deputy leader '''
        self._test_create_approval_request_as('user_02', allows_create=False)

    def test_create_approval_request_as_staff(self):
        ''' Test create approval request as staff '''
        self._test_create_approval_request_as('user_03', allows_create=False)

    def test_create_approval_request_as_member(self):
        ''' Test create approval request as member '''
        self._test_create_approval_request_as('user_04', allows_create=False)

    def test_create_approval_request_as_non_member(self):
        ''' Test create approval request as non-member '''
        self._test_create_approval_request_as('user_05', allows_create=False)

    def test_create_approval_request_as_lecturer(self):
        ''' Test create approval request as lecturer '''
        self._test_create_approval_request_as('lecturer', allows_create=False)

    def test_create_approval_request_as_support(self):
        ''' Test create approval request as support staff '''
        self._test_create_approval_request_as('support', allows_create=False)

    def test_create_approval_request_as_student_committee_member(self):
        ''' Test create approval request as student committee member '''
        self._test_create_approval_request_as('user_06', allows_create=False)

    def _test_create_approval_request_as(self, username, community=None, allows_create=False):
        ''' Test create approval request as different users '''
        self.client.login(username=username, password='12345678')

        if community is None:
            community = self.club_official
        response = self.client.post('/api/membership/approval-request/', {
            'community': community.id,
            'message': 'I\'d like to have my community approved.'
        })

        if allows_create:
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        else:
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.client.logout()

    def test_create_approval_request_duplicate(self):
        ''' Test create approval request duplicate '''
        self.client.login(username='user_01', password='12345678')

        # Pending approval request exists
        approval_request = ApprovalRequest.objects.create(community_id=self.club_unofficial.id, status='W')
        response = self.client.post('/api/membership/approval-request/', {
            'community': self.club_unofficial.id,
            'message': 'I\'d like to have my community approved.'
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Clean-up
        approval_request.delete()
        try:
            ApprovalRequest.objects.filter(community_id=self.club_unofficial.id)[0].delete()
        except IndexError:
            pass

        # Declined approval request exists
        approval_request = ApprovalRequest.objects.create(community_id=self.club_unofficial.id, status='D')
        response = self.client.post('/api/membership/approval-request/', {
            'community': self.club_unofficial.id,
            'message': 'I\'d like to have my community approved.'
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Clean-up
        approval_request.delete()
        try:
            ApprovalRequest.objects.filter(community_id=self.club_unofficial.id)[0].delete()
        except IndexError:
            pass

        # Accepted approval request exists
        approval_request = ApprovalRequest.objects.create(community_id=self.club_unofficial.id, status='A')
        response = self.client.post('/api/membership/approval-request/', {
            'community': self.club_unofficial.id,
            'message': 'I\'d like to have my community approved.'
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Clean-up
        approval_request.delete()
        try:
            ApprovalRequest.objects.filter(community_id=self.club_unofficial.id)[0].delete()
        except IndexError:
            pass

        self.client.logout()

    def test_create_approval_request_club_valid_through(self):
        ''' Test create approval request for club based on valid through date '''
        self.client.login(username='user_01', password='12345678')

        # 1 day early until advanced renewal availability
        club = Club.objects.create(
            name_th='ชุมนุมทดสอบคำขออนุมัติ พิเศษ 1',
            name_en='Approval Request Testing Club (Special 1)',
            is_official=True,
            valid_through=datetime.datetime.now().date() + CLUB_ADVANCED_RENEWAL + datetime.timedelta(days=1)
        )
        Membership.objects.create(community_id=club.id, user_id=self.user_01.id, position=3)
        response = self.client.post('/api/membership/approval-request/', {
            'community': club.id,
            'message': 'I\'d like to have my community approved.'
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Exact start date of advanced renewal availability
        club = Club.objects.create(
            name_th='ชุมนุมทดสอบคำขออนุมัติ พิเศษ 2',
            name_en='Approval Request Testing Club (Special 2)',
            is_official=True,
            valid_through=datetime.datetime.now().date() + CLUB_ADVANCED_RENEWAL
        )
        Membership.objects.create(community_id=club.id, user_id=self.user_01.id, position=3)
        response = self.client.post('/api/membership/approval-request/', {
            'community': club.id,
            'message': 'I\'d like to have my community approved.'
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # 1 day since advanced renewal availability
        club = Club.objects.create(
            name_th='ชุมนุมทดสอบคำขออนุมัติ พิเศษ 3',
            name_en='Approval Request Testing Club (Special 3)',
            is_official=True,
            valid_through=datetime.datetime.now().date() + CLUB_ADVANCED_RENEWAL - datetime.timedelta(days=1)
        )
        Membership.objects.create(community_id=club.id, user_id=self.user_01.id, position=3)
        response = self.client.post('/api/membership/approval-request/', {
            'community': club.id,
            'message': 'I\'d like to have my community approved.'
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.client.logout()

    def test_create_approval_request_event_unapproved(self):
        ''' Test create approval request on unapproved event '''
        self.client.login(username='user_01', password='12345678')

        event = Event.objects.get(pk=self.event.id)
        event.is_approved = False
        event.save()

        response = self.client.post('/api/membership/approval-request/', {
            'community': self.event.id,
            'message': 'I\'d like to have my event approved.'
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.client.logout()

    def test_create_approval_request_event_approved(self):
        ''' Test create approval request on approved event '''
        self.client.login(username='user_01', password='12345678')

        event = Event.objects.get(pk=self.event.id)
        event.is_approved = True
        event.save()

        response = self.client.post('/api/membership/approval-request/', {
            'community': self.event.id,
            'message': 'I\'d like to have my event approved.'
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.client.logout()

    def test_update_approval_request_as_leader(self):
        ''' Test update approval request as leader '''
        self._test_decline_approval_request_as('user_01', allows_update=False)
        self._test_accept_approval_request_as('user_01', allows_update=False)

    def test_update_approval_request_as_deputy_leader(self):
        ''' Test update approval request as deputy leader '''
        self._test_decline_approval_request_as('user_02', allows_update=False)
        self._test_accept_approval_request_as('user_02', allows_update=False)

    def test_update_approval_request_as_staff(self):
        ''' Test update approval request as staff '''
        self._test_decline_approval_request_as('user_03', allows_update=False)
        self._test_accept_approval_request_as('user_03', allows_update=False)

    def test_update_approval_request_as_member(self):
        ''' Test update approval request as member '''
        self._test_decline_approval_request_as('user_04', allows_update=False)
        self._test_accept_approval_request_as('user_04', allows_update=False)

    def test_update_approval_request_as_non_member(self):
        ''' Test update approval request as non-member '''
        self._test_decline_approval_request_as('user_05', allows_update=False)
        self._test_accept_approval_request_as('user_05', allows_update=False)

    def test_update_approval_request_as_lecturer(self):
        ''' Test update approval request as lecturer '''
        self._test_decline_approval_request_as('lecturer', allows_update=False)
        self._test_accept_approval_request_as('lecturer', allows_update=False)

    def test_update_approval_request_as_support(self):
        ''' Test update approval request as support staff '''
        self._test_decline_approval_request_as('support', allows_update=True)
        self._test_accept_approval_request_as('support', allows_update=True)

    def test_update_approval_request_as_student_committee_member(self):
        ''' Test update approval request as student committee member '''
        self._test_decline_approval_request_as('user_06', allows_update=True)
        self._test_accept_approval_request_as('user_06', allows_update=True)

    def _test_accept_approval_request_as(self, username, allows_update=False):
        ''' Test decline approval request as different users '''
        self.client.login(username=username, password='12345678')

        approval_request = ApprovalRequest.objects.create(community_id=self.club_unofficial.id)
        response = self.client.patch('/api/membership/approval-request/{}/'.format(approval_request.id), {
            'status': 'A'
        })

        if allows_update:
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data['status'], 'A')
            self.assertEqual(Club.objects.get(pk=self.club_unofficial.id).is_official, True)
            self.assertNotEqual(Club.objects.get(pk=self.club_unofficial.id).valid_through, None)
        else:
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.client.logout()

    def _test_decline_approval_request_as(self, username, allows_update=False):
        ''' Test decline approval request as different users '''
        self.client.login(username=username, password='12345678')

        approval_request = ApprovalRequest.objects.create(community_id=self.club_unofficial.id)
        response = self.client.patch('/api/membership/approval-request/{}/'.format(approval_request.id), {
            'status': 'D'
        })

        if allows_update:
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data['status'], 'D')
            self.assertEqual(Club.objects.get(pk=self.club_unofficial.id).is_official, False)
            self.assertEqual(Club.objects.get(pk=self.club_unofficial.id).valid_through, None)
        else:
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.client.logout()

    def test_illegal_update_approval_request(self):
        ''' Test illegal update approval request '''
        self.client.login(username='user_06', password='12345678')

        approval_request = ApprovalRequest.objects.create(community_id=self.club_unofficial.id, status='A')

        response = self.client.patch('/api/membership/approval-request/{}/'.format(approval_request.id), {
            'status': 'A'
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        response = self.client.patch('/api/membership/approval-request/{}/'.format(approval_request.id), {
            'status': 'D'
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        approval_request = ApprovalRequest.objects.create(community_id=self.club_unofficial.id, status='D')

        response = self.client.patch('/api/membership/approval-request/{}/'.format(approval_request.id), {
            'status': 'A'
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        response = self.client.patch('/api/membership/approval-request/{}/'.format(approval_request.id), {
            'status': 'D'
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.client.logout()

    def test_delete_approval_request_as_leader(self):
        ''' Test delete approval request as leader '''
        self._test_delete_approval_request_as('user_01', allows_delete=True)

    def test_delete_approval_request_as_deputy_leader(self):
        ''' Test delete approval request as deputy leader '''
        self._test_delete_approval_request_as('user_02', allows_delete=False)

    def test_delete_approval_request_as_staff(self):
        ''' Test delete approval request as staff '''
        self._test_delete_approval_request_as('user_03', allows_delete=False)

    def test_delete_approval_request_as_member(self):
        ''' Test delete approval request as member '''
        self._test_delete_approval_request_as('user_04', allows_delete=False)

    def test_delete_approval_request_as_non_member(self):
        ''' Test delete approval request as non-member '''
        self._test_delete_approval_request_as('user_05', allows_delete=False)

    def test_delete_approval_request_as_lecturer(self):
        ''' Test delete approval request as lecturer '''
        self._test_delete_approval_request_as('lecturer', allows_delete=False)

    def test_delete_approval_request_as_support(self):
        ''' Test delete approval request as support staff '''
        self._test_delete_approval_request_as('support', allows_delete=False)

    def test_delete_approval_request_as_student_committee_member(self):
        ''' Test delete approval request as student committee member '''
        self._test_delete_approval_request_as('user_06', allows_delete=False)

    def _test_delete_approval_request_as(self, username, allows_delete=False):
        ''' Test delete approval request as different users '''
        self.client.login(username=username, password='12345678')

        approval_request = ApprovalRequest.objects.create(community_id=self.club_unofficial.id)
        response = self.client.delete('/api/membership/approval-request/{}/'.format(approval_request.id))

        if allows_delete:
            self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        else:
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.client.logout()

    def test_delete_approval_request_accepted(self):
        ''' Test delete approval request that is already accepted '''
        self.client.login(username='user_01', password='12345678')

        approval_request = ApprovalRequest.objects.create(community_id=self.club_unofficial.id, status='A')
        response = self.client.delete('/api/membership/approval-request/{}/'.format(approval_request.id))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.client.logout()

    def test_delete_approval_request_declined(self):
        ''' Test delete approval request that is already declined '''
        self.client.login(username='user_01', password='12345678')

        approval_request = ApprovalRequest.objects.create(community_id=self.club_unofficial.id, status='D')
        response = self.client.delete('/api/membership/approval-request/{}/'.format(approval_request.id))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.client.logout()
