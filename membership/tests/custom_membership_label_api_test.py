'''
    Membership Application's Custom Membership Label API Test
    membership/tests/custom_membership_label_api_test.py
    @author Teerapat Kraisrisirikul (810Teams)
'''

from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from community.models import Club
from membership.models import Membership, CustomMembershipLabel


class CustomMembershipLabelAPITest(APITestCase):
    ''' Custom membership label API test '''
    def setUp(self):
        ''' Set up '''
        self.user_01 = get_user_model().objects.create_user(username='user_01', password='12345678', name='User One')
        self.user_02 = get_user_model().objects.create_user(username='user_02', password='12345678', name='User Two')
        self.user_03 = get_user_model().objects.create_user(username='user_03', password='12345678', name='User Three')
        self.user_04 = get_user_model().objects.create_user(username='user_04', password='12345678', name='User Four')
        self.user_05 = get_user_model().objects.create_user(username='user_05', password='12345678', name='User Five')
        self.user_06 = get_user_model().objects.create_user(username='user_06', password='12345678', name='User Six')
        self.club_public = Club.objects.create(
            name_th='ชุมนุมทดสอบชื่อตำแหน่ง สาธารณะ', name_en='Custom Membership Label Testing Club (Public)', is_publicly_visible=True
        )
        self.club_private = Club.objects.create(
            name_th='ชุมนุมทดสอบชื่อตำแหน่ง ส่วนตัว', name_en='Custom Membership Label Testing Club (Private)'
        )

        self.m1pub = Membership.objects.create(community_id=self.club_public.id, user_id=self.user_01.id, position=3)
        self.m2pub = Membership.objects.create(community_id=self.club_public.id, user_id=self.user_02.id, position=2)
        self.m3pub = Membership.objects.create(community_id=self.club_public.id, user_id=self.user_03.id, position=1)
        self.m4pub = Membership.objects.create(community_id=self.club_public.id, user_id=self.user_04.id, position=0)
        self.m5pub = Membership.objects.create(community_id=self.club_public.id, user_id=self.user_05.id, position=1)

        self.m1pri = Membership.objects.create(community_id=self.club_private.id, user_id=self.user_01.id, position=3)
        self.m2pri = Membership.objects.create(community_id=self.club_private.id, user_id=self.user_02.id, position=2)
        self.m3pri = Membership.objects.create(community_id=self.club_private.id, user_id=self.user_03.id, position=1)
        self.m4pri = Membership.objects.create(community_id=self.club_private.id, user_id=self.user_04.id, position=0)
        self.m5pri = Membership.objects.create(community_id=self.club_private.id, user_id=self.user_05.id, position=1)

        self.m5pub_label = CustomMembershipLabel.objects.create(membership_id=self.m5pub.id, label='Unlabeled')
        self.m5pri_label = CustomMembershipLabel.objects.create(membership_id=self.m5pri.id, label='Unlabeled')

    def test_list_custom_membership_label_authenticated(self):
        ''' Test list custom membership label authenticated '''
        self.client.login(username='user_06', password='12345678')

        response = self.client.get('/api/membership/membership/label/custom/')
        self.assertEqual(len(response.data), 2)

        self.client.logout()

    def test_list_custom_membership_label_unauthenticated(self):
        ''' Test list custom membership label unauthenticated '''
        response = self.client.get('/api/membership/membership/label/custom/')
        self.assertEqual(len(response.data), 1)

    def test_retrieve_custom_membership_label_authenticated(self):
        ''' Test retrieve custom membership label while authenticated '''
        self.client.login(username='user_06', password='12345678')

        response = self.client.get('/api/membership/membership/label/custom/{}/'.format(self.m5pub_label.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.get('/api/membership/membership/label/custom/{}/'.format(self.m5pri_label.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.client.logout()

    def test_retrieve_custom_membership_label_unauthenticated(self):
        ''' Test retrieve custom membership label while authenticated '''
        response = self.client.get('/api/membership/membership/label/custom/{}/'.format(self.m5pub_label.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.get('/api/membership/membership/label/custom/{}/'.format(self.m5pri_label.id))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_custom_membership_label_as_leader(self):
        ''' Test create custom membership label as leader '''
        self._test_create_custom_membership_label_as(
            'user_01',
            assign_leader=status.HTTP_400_BAD_REQUEST,
            assign_deputy_leader=status.HTTP_201_CREATED,
            assign_staff=status.HTTP_201_CREATED,
            assign_member=status.HTTP_400_BAD_REQUEST,
            assign_already_assigned=status.HTTP_400_BAD_REQUEST
        )

    def test_create_custom_membership_label_as_deputy_leader(self):
        ''' Test create custom membership label as deputy leader '''
        self._test_create_custom_membership_label_as(
            'user_02',
            assign_leader=status.HTTP_400_BAD_REQUEST,
            assign_deputy_leader=status.HTTP_201_CREATED,
            assign_staff=status.HTTP_201_CREATED,
            assign_member=status.HTTP_400_BAD_REQUEST,
            assign_already_assigned=status.HTTP_400_BAD_REQUEST
        )

    def test_create_custom_membership_label_as_staff(self):
        ''' Test create custom membership label as staff '''
        self._test_create_custom_membership_label_as(
            'user_03',
            assign_leader=status.HTTP_400_BAD_REQUEST,
            assign_deputy_leader=status.HTTP_400_BAD_REQUEST,
            assign_staff=status.HTTP_400_BAD_REQUEST,
            assign_member=status.HTTP_400_BAD_REQUEST,
            assign_already_assigned=status.HTTP_400_BAD_REQUEST
        )

    def test_create_custom_membership_label_as_member(self):
        ''' Test create custom membership label as member '''
        self._test_create_custom_membership_label_as(
            'user_04',
            assign_leader=status.HTTP_400_BAD_REQUEST,
            assign_deputy_leader=status.HTTP_400_BAD_REQUEST,
            assign_staff=status.HTTP_400_BAD_REQUEST,
            assign_member=status.HTTP_400_BAD_REQUEST,
            assign_already_assigned=status.HTTP_400_BAD_REQUEST
        )

    def test_create_custom_membership_label_as_non_member(self):
        ''' Test create custom membership label as non-member '''
        self._test_create_custom_membership_label_as(
            'user_06',
            assign_leader=status.HTTP_400_BAD_REQUEST,
            assign_deputy_leader=status.HTTP_400_BAD_REQUEST,
            assign_staff=status.HTTP_400_BAD_REQUEST,
            assign_member=status.HTTP_400_BAD_REQUEST,
            assign_already_assigned=status.HTTP_400_BAD_REQUEST
        )

    def _test_create_custom_membership_label_as(self, username, assign_leader=400, assign_deputy_leader=201,
                                                assign_staff=201, assign_member=400, assign_already_assigned=400):
        ''' Test create custom membership label as different membership positions '''
        self.client.login(username=username, password='12345678')

        response = self.client.post('/api/membership/membership/label/custom/', {
            'membership': self.m1pub.id,
            'label': 'Unlabeled'
        })
        self.assertEqual(response.status_code, assign_leader)

        response = self.client.post('/api/membership/membership/label/custom/', {
            'membership': self.m2pub.id,
            'label': 'Unlabeled'
        })
        self.assertEqual(response.status_code, assign_deputy_leader)

        response = self.client.post('/api/membership/membership/label/custom/', {
            'membership': self.m3pub.id,
            'label': 'Unlabeled'
        })
        self.assertEqual(response.status_code, assign_staff)

        response = self.client.post('/api/membership/membership/label/custom/', {
            'membership': self.m4pub.id,
            'label': 'Unlabeled'
        })
        self.assertEqual(response.status_code, assign_member)

        response = self.client.post('/api/membership/membership/label/custom/', {
            'membership': self.m5pub.id,
            'label': 'Unlabeled'
        })
        self.assertEqual(response.status_code, assign_already_assigned)

        self.client.logout()

    def test_update_custom_membership_label_as_leader(self):
        ''' Test update custom membership label as leader '''
        self._test_update_custom_membership_label_as('user_01', allows_update=True)

    def test_update_custom_membership_label_as_deputy_leader(self):
        ''' Test update custom membership label as deputy leader '''
        self._test_update_custom_membership_label_as('user_02', allows_update=True)

    def test_update_custom_membership_label_as_staff(self):
        ''' Test update custom membership label as staff '''
        self._test_update_custom_membership_label_as('user_03', allows_update=False)

    def test_update_custom_membership_label_as_member(self):
        ''' Test update custom membership label as member '''
        self._test_update_custom_membership_label_as('user_04', allows_update=False)

    def test_update_custom_membership_label_as_non_member(self):
        ''' Test update custom membership label as non-member '''
        self._test_update_custom_membership_label_as('user_06', allows_update=False)

    def _test_update_custom_membership_label_as(self, username, allows_update=True):
        ''' Test update custom membership label as different membership positions '''
        self.client.login(username=username, password='12345678')

        response = self.client.patch('/api/membership/membership/label/custom/{}/'.format(self.m5pub_label.id), {
            'label': 'New Label'
        })

        if allows_update:
            self.assertEqual(response.status_code, status.HTTP_200_OK)
        else:
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        response = self.client.patch('/api/membership/membership/label/custom/{}/'.format(self.m5pri_label.id), {
            'label': 'New Label'
        })

        if allows_update:
            self.assertEqual(response.status_code, status.HTTP_200_OK)
        else:
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.client.logout()

    def test_delete_custom_membership_label_as_leader(self):
        ''' Test delete custom membership label as leader '''
        self._test_delete_custom_membership_label_as('user_01', allows_delete=True)

    def test_delete_custom_membership_label_as_deputy_leader(self):
        ''' Test delete custom membership label as deputy leader '''
        self._test_delete_custom_membership_label_as('user_02', allows_delete=True)

    def test_delete_custom_membership_label_as_staff(self):
        ''' Test delete custom membership label as staff '''
        self._test_delete_custom_membership_label_as('user_03', allows_delete=False)

    def test_delete_custom_membership_label_as_member(self):
        ''' Test delete custom membership label as member '''
        self._test_delete_custom_membership_label_as('user_04', allows_delete=False)

    def test_delete_custom_membership_label_as_non_member(self):
        ''' Test delete custom membership label as non-member '''
        self._test_delete_custom_membership_label_as('user_06', allows_delete=False)

    def _test_delete_custom_membership_label_as(self, username, allows_delete=True):
        ''' Test delete custom membership label as different membership positions '''
        self.client.login(username=username, password='12345678')

        response = self.client.delete('/api/membership/membership/label/custom/{}/'.format(self.m5pub_label.id))

        if allows_delete:
            self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        else:
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        response = self.client.delete('/api/membership/membership/label/custom/{}/'.format(self.m5pri_label.id))

        if allows_delete:
            self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        else:
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.client.logout()
