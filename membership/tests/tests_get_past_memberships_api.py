'''
    Membership Application's Get Past Memberships API Test
    membership/tests/tests_get_past_memberships_api.py
    @author Teerapat Kraisrisirikul (810Teams)
'''

from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from community.models import Club
from membership.models import Membership

import time


class GetPastMembershipsAPITest(APITestCase):
    ''' Get past memberships API test '''
    def setUp(self):
        ''' Set up '''
        self.user_01 = get_user_model().objects.create_user(username='user_01', password='12345678', name='User One')
        self.user_02 = get_user_model().objects.create_user(username='user_02', password='12345678', name='User Two')
        self.user_03 = get_user_model().objects.create_user(username='user_03', password='12345678', name='User Three')
        self.user_04 = get_user_model().objects.create_user(username='user_04', password='12345678', name='User Four')
        self.user_05 = get_user_model().objects.create_user(username='user_05', password='12345678', name='User Five')

        self.club_public = Club.objects.create(
            name_th='ชุมนุมทดสอบประวัติสมาชิก สาธารณะ',
            name_en='Past Membership Testing Club (Public)',
            is_publicly_visible=True
        )
        self.club_private = Club.objects.create(
            name_th='ชุมนุมทดสอบประวัติสมาชิก ส่วนตัว',
            name_en='Past Membership Testing Club (Private)',
            is_publicly_visible=False
        )

        self.m1pub = Membership.objects.create(community_id=self.club_public.id, user_id=self.user_01.id, position=3)
        self.m2pub = Membership.objects.create(community_id=self.club_public.id, user_id=self.user_02.id, position=0)
        self.m1pri = Membership.objects.create(community_id=self.club_private.id, user_id=self.user_01.id, position=3)
        self.m2pri = Membership.objects.create(community_id=self.club_private.id, user_id=self.user_02.id, position=0)

        time.sleep(1)

        self.m2pub.position = '2'
        self.m2pub.save()
        self.m2pri.position = '2'
        self.m2pri.save()

        time.sleep(1)

        self.m2pub.position = '1'
        self.m2pub.save()
        self.m2pri.position = '1'
        self.m2pri.save()

        time.sleep(1)

        self.m2pub.status = 'L'
        self.m2pub.save()
        self.m2pri.status = 'L'
        self.m2pri.save()

    def test_retrieve_past_membership_authenticated(self):
        ''' Test retrieve past membership while authenticated '''
        self.client.login(username='user_05', password='12345678')

        response = self.client.get('/api/membership/membership/past/{}/'.format(self.user_02.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

        self.client.logout()

    def test_retrieve_past_membership_unauthenticated(self):
        ''' Test retrieve past membership while unauthenticated '''
        response = self.client.get('/api/membership/membership/past/{}/'.format(self.user_02.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_validate_past_membership(self):
        ''' Test validate past membership algorithm '''
        response = self.client.get('/api/membership/membership/past/{}/'.format(self.user_02.id))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]['community_id'], self.club_public.id)
        self.assertEqual(response.data[0]['community_type'], 'club')

        self.assertLess(response.data[0]['start_datetime'], response.data[0]['end_datetime'])
        self.assertEqual(response.data[0]['position'], 2)
        self.assertLess(response.data[0]['position_start_datetime'], response.data[0]['position_end_datetime'])

        self.assertLess(response.data[0]['start_datetime'], response.data[0]['position_start_datetime'])
        self.assertLess(response.data[0]['position_end_datetime'], response.data[0]['end_datetime'])

    def test_create_past_membership(self):
        ''' Test create past membership '''
        self.client.login(username='user_05', password='12345678')

        response = self.client.post('/api/membership/membership/past/{}/'.format(self.user_02.id), {})
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        self.client.logout()

    def test_update_past_membership(self):
        ''' Test update past membership '''
        self.client.login(username='user_05', password='12345678')

        response = self.client.put('/api/membership/membership/past/{}/'.format(self.user_02.id), {})
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.patch('/api/membership/membership/past/{}/'.format(self.user_02.id), {})
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        self.client.logout()

    def test_delete_past_membership(self):
        ''' Test update past membership '''
        self.client.login(username='user_05', password='12345678')

        response = self.client.delete('/api/membership/membership/past/{}/'.format(self.user_02.id), {})
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        self.client.logout()
