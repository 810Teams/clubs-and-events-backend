'''
    Membership Application's Membership API Test
    membership/tests/tests_membership_api.py
    @author Teerapat Kraisrisirikul (810Teams)
'''

from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from community.models import Club
from membership.models import Membership


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

    def test_list_membership_authenticated(self):
        ''' Test list memberships while authenticated '''
        self.client.login(username='user_05', password='12345678')

        response = self.client.get('/api/membership/membership/')
        self.assertEqual(len(response.data), self.memberships_public + self.memberships_private)

        self.client.logout()

    def test_list_membership_unauthenticated(self):
        ''' Test list memberships while not authenticated '''
        response = self.client.get('/api/membership/membership/')
        self.assertEqual(len(response.data), self.memberships_public)

    def test_retrieve_membership_authenticated(self):
        ''' Test retrieve membership while authenticated '''
        self.client.login(username='user_05', password='12345678')

        response = self.client.get('/api/membership/membership/{}/'.format(self.m1pub.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.get('/api/membership/membership/{}/'.format(self.m1pri.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.client.logout()

    def test_retrieve_membership_unauthenticated(self):
        ''' Test retrieve membership while not authenticated '''
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
