'''
    Asset Application's Comment API Test
    asset/tests/tests_comment_api.py
    @author Teerapat Kraisrisirikul (810Teams)
'''

from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from asset.models import Comment
from community.models import Club, Event, CommunityEvent

import datetime

from core.utils.general import get_random_string


class CommentAPITest(APITestCase):
    ''' Comment API test '''
    def setUp(self):
        ''' Set up '''
        self.user = get_user_model().objects.create_user(username='user', password='12345678', name='User')

        self.club_public = Club.objects.create(
            name_th='ชุมนุมทดสอบความคิดเห็น สาธารณะ', name_en='Comment Testing Club (Public)',
            is_publicly_visible=True, is_official=True
        )
        self.club_private = Club.objects.create(
            name_th='ชุมนุมทดสอบความคิดเห็น ส่วนตัว', name_en='Comment Testing Club (Private)',
            is_publicly_visible=False, is_official=True
        )
        self.event_public = Event.objects.create(
            name_th='กิจกรรมทดสอบความคิดเห็น สาธารณะ', name_en='Comment Testing Event (Public)',
            is_approved=True, location='L207 IT KMITL',
            start_date=datetime.date(2020, 12, 1), end_date=datetime.date(2020, 12, 2),
            start_time=datetime.time(9, 0, 0), end_time=datetime.time(17, 0, 0), is_publicly_visible=True
        )
        self.event_private = Event.objects.create(
            name_th='กิจกรรมทดสอบความคิดเห็น ส่วนตัว', name_en='Comment Testing Event (Private)',
            is_approved=True, location='L207 IT KMITL',
            start_date=datetime.date(2020, 12, 1), end_date=datetime.date(2020, 12, 2),
            start_time=datetime.time(9, 0, 0), end_time=datetime.time(17, 0, 0), is_publicly_visible=False
        )

    def test_list_comment_event_authenticated(self):
        ''' Test list comment on events while authenticated '''
        self.client.login(username='user', password='12345678')

        Comment.objects.create(text='Greetings!', written_by='Guest', event_id=self.event_public.id)
        Comment.objects.create(text='Hello!', written_by='Guest', event_id=self.event_public.id)
        Comment.objects.create(text='Hi!', written_by='Guest', event_id=self.event_private.id)

        response = self.client.get('/api/asset/comment/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)

        self.client.logout()

    def test_list_comment_event_unauthenticated(self):
        ''' Test list comment on events while unauthenticated '''
        Comment.objects.create(text='Greetings!', written_by='Guest', event_id=self.event_public.id)
        Comment.objects.create(text='Hello!', written_by='Guest', event_id=self.event_public.id)
        Comment.objects.create(text='Hi!', written_by='Guest', event_id=self.event_private.id)

        response = self.client.get('/api/asset/comment/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_list_comment_community_event_authenticated(self):
        ''' Test list comment on community events while authenticated '''
        self.client.login(username='user', password='12345678')

        self._test_list_comment_community_event(
            is_publicly_visible=True, created_under_id=self.club_public.id, expected_length=1
        )
        self._test_list_comment_community_event(
            is_publicly_visible=True, created_under_id=self.club_private.id, expected_length=1
        )
        self._test_list_comment_community_event(
            is_publicly_visible=False, created_under_id=self.club_public.id, expected_length=1
        )
        self._test_list_comment_community_event(
            is_publicly_visible=False, created_under_id=self.club_private.id, expected_length=1
        )

        self.client.logout()

    def test_list_comment_community_event_unauthenticated(self):
        ''' Test list comment on community events while unauthenticated '''
        self._test_list_comment_community_event(
            is_publicly_visible=True, created_under_id=self.club_public.id, expected_length=1
        )
        self._test_list_comment_community_event(
            is_publicly_visible=True, created_under_id=self.club_private.id, expected_length=0
        )
        self._test_list_comment_community_event(
            is_publicly_visible=False, created_under_id=self.club_public.id, expected_length=0
        )
        self._test_list_comment_community_event(
            is_publicly_visible=False, created_under_id=self.club_private.id, expected_length=0
        )

    def _test_list_comment_community_event(self, is_publicly_visible=True, created_under_id=int(), expected_length=0):
        ''' Test list comment on community events '''
        community_event = CommunityEvent.objects.create(
            name_th='กิจกรรมชุมนุมทดสอบความคิดเห็น พิเศษ - {}'.format(get_random_string(length=16)),
            name_en='Comment Testing Club Event (Special) - {}'.format(get_random_string(length=16)),
            is_approved=True, location='L207 IT KMITL',
            start_date=datetime.date(2020, 12, 1), end_date=datetime.date(2020, 12, 2),
            start_time=datetime.time(9, 0, 0), end_time=datetime.time(17, 0, 0),
            is_publicly_visible=is_publicly_visible, created_under_id=created_under_id,
            allows_outside_participators=True
        )

        comment = Comment.objects.create(text='Greetings!', written_by='Guest', event_id=community_event.id)

        response = self.client.get('/api/asset/comment/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), expected_length)

        comment.delete()
