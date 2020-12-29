'''
    Membership Application's Membership Log API Test
    membership/tests/tests_membership_log_api.py
    @author Teerapat Kraisrisirikul (810Teams)
'''

from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from community.models import Club
from membership.models import Membership, MembershipLog

import time


class MembershipLogAPITest(APITestCase):
    ''' Membership log API test '''
    def setUp(self):
        ''' Set up '''
        self.user_01 = get_user_model().objects.create_user(username='user_01', password='12345678', name='User One')
        self.user_02 = get_user_model().objects.create_user(username='user_02', password='12345678', name='User Two')
        self.user_03 = get_user_model().objects.create_user(username='user_03', password='12345678', name='User Three')
        self.user_04 = get_user_model().objects.create_user(username='user_04', password='12345678', name='User Four')
        self.user_05 = get_user_model().objects.create_user(username='user_05', password='12345678', name='User Five')
        self.club_public = Club.objects.create(
            name_th='ชุมนุมทดสอบประวัติสมาชิก สาธารณะ', name_en='Membership Log Testing Club (Public)',
            is_publicly_visible=True
        )
        self.club_private = Club.objects.create(
            name_th='ชุมนุมทดสอบประวัติสมาชิก ส่วนตัว', name_en='Membership Log Testing Club (Private)'
        )

        self.m1pub = Membership.objects.create(community_id=self.club_public.id, user_id=self.user_01.id, position=3)
        self.m2pub = Membership.objects.create(community_id=self.club_public.id, user_id=self.user_02.id, position=2)
        self.m3pub = Membership.objects.create(community_id=self.club_public.id, user_id=self.user_03.id, position=1)
        self.m4pub = Membership.objects.create(community_id=self.club_public.id, user_id=self.user_04.id, position=0)

        self.m1pri = Membership.objects.create(community_id=self.club_private.id, user_id=self.user_01.id, position=3)
        self.m2pri = Membership.objects.create(community_id=self.club_private.id, user_id=self.user_02.id, position=2)
        self.m3pri = Membership.objects.create(community_id=self.club_private.id, user_id=self.user_03.id, position=1)
        self.m4pri = Membership.objects.create(community_id=self.club_private.id, user_id=self.user_04.id, position=0)

    def test_list_membership_log_authenticated(self):
        ''' Test list membership log while authenticated '''
        self.client.login(username='user_05', password='12345678')

        response = self.client.get('/api/membership/membership/log/')
        self.assertEqual(len(response.data), 8)

        self.client.logout()

    def test_list_membership_log_unauthenticated(self):
        ''' Test list membership log while unauthenticated '''
        response = self.client.get('/api/membership/membership/log/')
        self.assertEqual(len(response.data), 4)

    def test_retrieve_membership_log_authenticated(self):
        ''' Test retrieve membership log while authenticated '''
        self.client.login(username='user_05', password='12345678')

        ref = MembershipLog.objects.filter(membership_id=self.m1pub.id)[0].id
        response = self.client.get('/api/membership/membership/log/{}/'.format(ref))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        ref = MembershipLog.objects.filter(membership_id=self.m1pri.id)[0].id
        response = self.client.get('/api/membership/membership/log/{}/'.format(ref))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.client.logout()

    def test_retrieve_membership_log_unauthenticated(self):
        ''' Test retrieve membership log while unauthenticated '''
        ref = MembershipLog.objects.filter(membership_id=self.m1pub.id)[0].id
        response = self.client.get('/api/membership/membership/log/{}/'.format(ref))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        ref = MembershipLog.objects.filter(membership_id=self.m1pri.id)[0].id
        response = self.client.get('/api/membership/membership/log/{}/'.format(ref))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_auto_create_membership_log(self):
        ''' Test auto create membership log '''
        logs = MembershipLog.objects.filter(membership_id=self.m2pub.id)
        self.assertEqual(len(logs), 1)
        self.assertEqual(logs[len(logs) - 1].status, 'A')
        self.assertEqual(logs[len(logs) - 1].position, 2)

        time.sleep(1)

        self.m2pub.status = 'R'
        self.m2pub.save()
        logs = MembershipLog.objects.filter(membership_id=self.m2pub.id)
        self.assertEqual(len(logs), 2)
        self.assertEqual(logs[len(logs) - 1].status, 'R')
        self.assertEqual(logs[len(logs) - 1].position, 2)

        time.sleep(1)

        self.m2pub.status = 'A'
        self.m2pub.save()
        logs = MembershipLog.objects.filter(membership_id=self.m2pub.id)
        self.assertEqual(len(logs), 3)
        self.assertEqual(logs[len(logs) - 1].status, 'A')
        self.assertEqual(logs[len(logs) - 1].position, 2)

        time.sleep(1)

        self.m2pub.position = 1
        self.m2pub.save()
        logs = MembershipLog.objects.filter(membership_id=self.m2pub.id)
        self.assertEqual(len(logs), 4)
        self.assertEqual(logs[len(logs) - 1].status, 'A')
        self.assertEqual(logs[len(logs) - 1].position, 1)

        time.sleep(1)

        self.m2pub.position = 2
        self.m2pub.save()
        logs = MembershipLog.objects.filter(membership_id=self.m2pub.id)
        self.assertEqual(len(logs), 5)
        self.assertEqual(logs[len(logs) - 1].status, 'A')
        self.assertEqual(logs[len(logs) - 1].position, 2)

    def test_create_membership_log(self):
        ''' Test create membership log '''
        self.client.login(username='user_01', password='12345678')

        response = self.client.post('/api/membership/membership/log/', {})
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        self.client.logout()

    def test_update_membership_log(self):
        ''' Test update membership log '''
        self.client.login(username='user_01', password='12345678')

        ref = MembershipLog.objects.filter(membership_id=self.m1pub.id)[0].id
        response = self.client.patch('/api/membership/membership/log/{}/'.format(ref), {})
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        self.client.logout()

    def test_delete_membership_log(self):
        ''' Test delete membership log '''
        self.client.login(username='user_01', password='12345678')

        ref = MembershipLog.objects.filter(membership_id=self.m1pub.id)[0].id
        response = self.client.delete('/api/membership/membership/log/{}/'.format(ref))
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        self.client.logout()
