'''
    Membership Application's Advisory API Test
    membership/tests/tests_advisory_api.py
    @author Teerapat Kraisrisirikul (810Teams)
'''

from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from community.models import Club, Event, Lab, CommunityEvent
from membership.models import Membership, Advisory
from user.models import StudentCommitteeAuthority

import datetime


class AdvisoryAPITest(APITestCase):
    ''' Advisory API test '''
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
        self.lecturer_03 = get_user_model().objects.create_user(
            username='lecturer_03', password='12345678', name='Prof.Lazy Man', user_group='lecturer'
        )
        self.support_staff = get_user_model().objects.create_user(
            username='support', password='12345678', name='Mr.Supporter', user_group='support'
        )
        self.club_public = Club.objects.create(
            name_th='ชุมนุมทดสอบที่ปรึกษา สาธารณะ', name_en='Advisory Testing Club (Public)', is_publicly_visible=True
        )
        self.club_private = Club.objects.create(
            name_th='ชุมนุมทดสอบที่ปรึกษา ส่วนตัว', name_en='Advisory Testing Club (Private)'
        )
        self.event = Event.objects.create(
            name_th='กิจกรรมทดสอบที่ปรึกษา',
            name_en='Advisory Testing Event',
            is_approved=True,
            location='L207 IT KMITL',
            start_date=datetime.date(2020, 12, 1),
            end_date=datetime.date(2020, 12, 2),
            start_time=datetime.time(9, 0, 0),
            end_time=datetime.time(17, 0, 0)
        )
        self.lab = Lab.objects.create(name_th='ห้องปฏิบัติการทดสอบที่ปรึกษา', name_en='Advisory Testing Lab')
        self.community_event = CommunityEvent.objects.create(
            name_th='กิจกรรมชุมนุมทดสอบที่ปรึกษา',
            name_en='Advisory Testing Club Event',
            is_approved=True,
            location='L207 IT KMITL',
            start_date=datetime.date(2020, 12, 1),
            end_date=datetime.date(2020, 12, 2),
            start_time=datetime.time(9, 0, 0),
            end_time=datetime.time(17, 0, 0),
            created_under_id=self.club_public.id
        )

        self.m1pub = Membership.objects.create(community_id=self.club_public.id, user_id=self.user_01.id, position=3)
        self.m2pub = Membership.objects.create(community_id=self.club_public.id, user_id=self.user_02.id, position=2)
        self.m3pub = Membership.objects.create(community_id=self.club_public.id, user_id=self.user_03.id, position=1)
        self.m4pub = Membership.objects.create(community_id=self.club_public.id, user_id=self.user_04.id, position=0)

        self.m1pri = Membership.objects.create(community_id=self.club_private.id, user_id=self.user_01.id, position=3)
        self.m2pri = Membership.objects.create(community_id=self.club_private.id, user_id=self.user_02.id, position=2)
        self.m3pri = Membership.objects.create(community_id=self.club_private.id, user_id=self.user_03.id, position=1)
        self.m4pri = Membership.objects.create(community_id=self.club_private.id, user_id=self.user_04.id, position=0)

    def test_list_advisory_authenticated(self):
        ''' Test list advisory while authenticated '''
        self.client.login(username='user_05', password='12345678')

        Advisory.objects.create(
            advisor_id=self.lecturer_01.id, community_id=self.club_public.id,
            start_date=datetime.date(2020, 1, 1), end_date=datetime.date(2020, 6, 1)
        )
        Advisory.objects.create(
            advisor_id=self.lecturer_02.id, community_id=self.club_private.id,
            start_date=datetime.date(2020, 1, 1), end_date=datetime.date(2020, 6, 1)
        )
        response = self.client.get('/api/membership/advisory/')
        self.assertEqual(len(response.data), 2)

        self.client.logout()

    def test_list_advisory_unauthenticated(self):
        ''' Test list advisory while unauthenticated '''
        Advisory.objects.create(
            advisor_id=self.lecturer_01.id, community_id=self.club_public.id,
            start_date=datetime.date(2020, 1, 1), end_date=datetime.date(2020, 6, 1)
        )
        Advisory.objects.create(
            advisor_id=self.lecturer_02.id, community_id=self.club_private.id,
            start_date=datetime.date(2020, 1, 1), end_date=datetime.date(2020, 6, 1)
        )
        response = self.client.get('/api/membership/advisory/')
        self.assertEqual(len(response.data), 1)

    def test_retrieve_advisory_authenticated(self):
        ''' Test retrieve advisory while authenticated '''
        self.client.login(username='user_05', password='12345678')

        advisory = Advisory.objects.create(
            advisor_id=self.lecturer_01.id, community_id=self.club_public.id,
            start_date=datetime.date(2020, 1, 1), end_date=datetime.date(2020, 6, 1)
        )
        response = self.client.get('/api/membership/advisory/{}/'.format(advisory.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        advisory = Advisory.objects.create(
            advisor_id=self.lecturer_01.id, community_id=self.club_private.id,
            start_date=datetime.date(2020, 1, 1), end_date=datetime.date(2020, 6, 1)
        )
        response = self.client.get('/api/membership/advisory/{}/'.format(advisory.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.client.logout()

    def test_retrieve_advisory_unauthenticated(self):
        ''' Test retrieve advisory while unauthenticated '''
        advisory = Advisory.objects.create(
            advisor_id=self.lecturer_01.id, community_id=self.club_public.id,
            start_date=datetime.date(2020, 1, 1), end_date=datetime.date(2020, 6, 1)
        )
        response = self.client.get('/api/membership/advisory/{}/'.format(advisory.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        advisory = Advisory.objects.create(
            advisor_id=self.lecturer_01.id, community_id=self.club_private.id,
            start_date=datetime.date(2020, 1, 1), end_date=datetime.date(2020, 6, 1)
        )
        response = self.client.get('/api/membership/advisory/{}/'.format(advisory.id))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_advisory_as_student(self):
        ''' Test create advisory as normal student '''
        self._test_create_advisory_as('user_01', allows_create=False)

    def test_create_advisory_as_lecturer(self):
        ''' Test create advisory as lecturer '''
        self._test_create_advisory_as('lecturer_01', allows_create=False)

    def test_create_advisory_as_support_staff(self):
        ''' Test create advisory as support staff '''
        self._test_create_advisory_as('support', allows_create=True)

    def test_create_advisory_as_student_committee_member(self):
        ''' Test create advisory as student committee member '''
        StudentCommitteeAuthority.objects.create(
            user_id=self.user_05.id, start_date=datetime.date(1970, 1, 1), end_date=datetime.date(2099, 1, 1)
        )
        self._test_create_advisory_as('user_05', allows_create=True)

    def _test_create_advisory_as(self, username, allows_create=False):
        ''' Test create advisory as different users '''
        self.client.login(username=username, password='12345678')

        response = self.client.post('/api/membership/advisory/', {
            'advisor': self.lecturer_01.id,
            'community': self.club_public.id,
            'start_date': '2020-01-01',
            'end_date': '2020-06-01'
        })

        if allows_create:
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        else:
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.client.logout()

    def test_create_advisory_with_student(self):
        ''' Test create advisory with student as advisor '''
        self._test_create_advisory_with(self.user_01, allows_create=False)

    def test_create_advisory_with_lecturer(self):
        ''' Test create advisory with lecturer as advisor '''
        self._test_create_advisory_with(self.lecturer_01, allows_create=True)

    def test_create_advisory_with_support_staff(self):
        ''' Test create advisory with support staff as advisor '''
        self._test_create_advisory_with(self.support_staff, allows_create=False)

    def _test_create_advisory_with(self, advisor, allows_create=False):
        ''' Test create advisory with different user groups '''
        self.client.login(username='support', password='12345678')

        response = self.client.post('/api/membership/advisory/', {
            'advisor': advisor.id,
            'community': self.club_public.id,
            'start_date': '2020-01-01',
            'end_date': '2020-06-01'
        })

        if allows_create:
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        else:
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.client.logout()

    def test_create_advisory_on_club(self):
        ''' Test create advisory on club '''
        self._test_create_advisory_on(self.club_public, allows_create=True)

    def test_create_advisory_on_event(self):
        ''' Test create advisory on event '''
        self._test_create_advisory_on(self.event, allows_create=True)

    def test_create_advisory_on_lab(self):
        ''' Test create advisory on lab '''
        self._test_create_advisory_on(self.lab, allows_create=False)

    def test_create_advisory_on_community_event(self):
        ''' Test create advisory on community event '''
        self._test_create_advisory_on(self.community_event, allows_create=False)

    def _test_create_advisory_on(self, community, allows_create=False):
        ''' Test create advisory on different community types '''
        self.client.login(username='support', password='12345678')

        response = self.client.post('/api/membership/advisory/', {
            'advisor': self.lecturer_01.id,
            'community': community.id,
            'start_date': '2020-01-01',
            'end_date': '2020-06-01'
        })

        if allows_create:
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        else:
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.client.logout()

    def test_create_advisory_overlap(self):
        ''' Test create advisory overlapping each other '''
        self.client.login(username='support', password='12345678')

        # Initial advisory (Advisory 1; Jan-Mar 2020)
        self._test_create_advisory('2020-01-01', '2020-03-31', allows_create=True)

        # End date 2-day overlapped
        self._test_create_advisory('2020-03-30', '2020-06-30', allows_create=False)

        # End date 1-day overlapped
        self._test_create_advisory('2020-03-31', '2020-06-30', allows_create=False)

        # No end date overlap (Advisory 2; Apr-Jun 2020)
        self._test_create_advisory('2020-04-01', '2020-06-30', allows_create=True)

        # Start date 2-day overlapped
        self._test_create_advisory('2019-10-01', '2020-01-02', allows_create=False)

        # Start date 1-day overlapped
        self._test_create_advisory('2019-10-01', '2020-01-01', allows_create=False)

        # No start date overlapped (Advisory 3; Oct-Dec 2019)
        self._test_create_advisory('2019-10-01', '2019-12-31', allows_create=True)

        # Inside overlapped
        self._test_create_advisory('2020-01-02', '2020-03-30', allows_create=False)

        # Outside overlapped
        self._test_create_advisory('2019-12-31', '2020-04-01', allows_create=False)

        # Exact overlapped
        self._test_create_advisory('2020-01-01', '2020-03-31', allows_create=False)

        self.client.logout()

    def _test_create_advisory(self, start_date, end_date, lecturer=None, community=None, allows_create=True):
        ''' Test create advisory '''
        if lecturer is None:
            lecturer = self.lecturer_01
        if community is None:
            community = self.club_public

        response = self.client.post('/api/membership/advisory/', {
            'advisor': lecturer.id,
            'community': community.id,
            'start_date': start_date,
            'end_date': end_date
        })

        if allows_create:
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        else:
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_advisory_as_student(self):
        ''' Test update advisory as normal student '''
        self._test_update_advisory_as('user_01')

    def test_update_advisory_as_lecturer(self):
        ''' Test update advisory as lecturer '''
        self._test_update_advisory_as('lecturer_01')

    def test_update_advisory_as_support_staff(self):
        ''' Test update advisory as support staff '''
        self._test_update_advisory_as('support')

    def test_update_advisory_as_student_committee_member(self):
        ''' Test update advisory as student committee member '''
        StudentCommitteeAuthority.objects.create(
            user_id=self.user_05.id, start_date=datetime.date(1970, 1, 1), end_date=datetime.date(2099, 1, 1)
        )
        self._test_update_advisory_as('user_05')

    def _test_update_advisory_as(self, username):
        ''' Test update advisory as different user groups '''
        self.client.login(username=username, password='12345678')

        advisory = Advisory.objects.create(
            advisor_id=self.lecturer_01.id, community_id=self.club_public.id,
            start_date=datetime.date(2020, 1, 1), end_date=datetime.date(2020, 6, 1)
        )
        response = self.client.patch('/api/membership/advisory/{}/'.format(advisory.id), {
            'start_date': '2020-01-01',
            'end_date': '2020-06-31'
        })
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        self.client.logout()

    def test_delete_advisory_as_student(self):
        ''' Test delete advisory as normal student '''
        self._test_delete_advisory_as('user_01', allows_delete=False)

    def test_delete_advisory_as_lecturer(self):
        ''' Test delete advisory as lecturer '''
        self._test_delete_advisory_as('lecturer_01', allows_delete=False)

    def test_delete_advisory_as_support_staff(self):
        ''' Test delete advisory as support staff '''
        self._test_delete_advisory_as('support', allows_delete=True)

    def test_delete_advisory_as_student_committee_member(self):
        ''' Test delete advisory as student committee member '''
        StudentCommitteeAuthority.objects.create(
            user_id=self.user_05.id, start_date=datetime.date(1970, 1, 1), end_date=datetime.date(2099, 1, 1)
        )
        self._test_delete_advisory_as('user_05', allows_delete=True)

    def _test_delete_advisory_as(self, username, allows_delete=False):
        ''' Test delete advisory as different user groups '''
        self.client.login(username=username, password='12345678')

        advisory = Advisory.objects.create(
            advisor_id=self.lecturer_01.id, community_id=self.club_public.id,
            start_date=datetime.date(2020, 1, 1), end_date=datetime.date(2020, 6, 1)
        )
        response = self.client.delete('/api/membership/advisory/{}/'.format(advisory.id))

        if allows_delete:
            self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        else:
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.client.logout()
