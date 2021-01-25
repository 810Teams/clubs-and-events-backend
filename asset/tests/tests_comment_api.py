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
from core.utils.general import get_random_string
from membership.models import Membership

import datetime


class CommentAPITest(APITestCase):
    ''' Comment API test '''
    def setUp(self):
        ''' Set up '''
        self.user_01 = get_user_model().objects.create_user(username='user_01', password='12345678', name='User One')
        self.user_02 = get_user_model().objects.create_user(username='user_02', password='12345678', name='User One')
        self.user_03 = get_user_model().objects.create_user(username='user_03', password='12345678', name='User One')
        self.user_04 = get_user_model().objects.create_user(username='user_04', password='12345678', name='User One')
        self.user_05 = get_user_model().objects.create_user(username='user_05', password='12345678', name='User One')

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

        Membership.objects.create(community_id=self.event_public.id, user_id=self.user_01.id, position=3)
        Membership.objects.create(community_id=self.event_public.id, user_id=self.user_02.id, position=2)
        Membership.objects.create(community_id=self.event_public.id, user_id=self.user_03.id, position=1)
        Membership.objects.create(community_id=self.event_public.id, user_id=self.user_04.id, position=0)

    def test_list_comment_event_authenticated(self):
        ''' Test list comment on events while authenticated '''
        self.client.login(username='user_01', password='12345678')

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
        self.client.login(username='user_01', password='12345678')

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

    def test_retrieve_comment_event_authenticated(self):
        ''' Test retrieve comment on events while authenticated '''
        self.client.login(username='user_01', password='12345678')

        comment = Comment.objects.create(text='Greetings!', written_by='Guest', event_id=self.event_public.id)
        response = self.client.get('/api/asset/comment/{}/'.format(comment.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        comment = Comment.objects.create(text='Hi!', written_by='Guest', event_id=self.event_private.id)
        response = self.client.get('/api/asset/comment/{}/'.format(comment.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.client.logout()

    def test_retrieve_comment_event_unauthenticated(self):
        ''' Test retrieve comment on events while unauthenticated '''
        comment = Comment.objects.create(text='Greetings!', written_by='Guest', event_id=self.event_public.id)
        response = self.client.get('/api/asset/comment/{}/'.format(comment.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        comment = Comment.objects.create(text='Hi!', written_by='Guest', event_id=self.event_private.id)
        response = self.client.get('/api/asset/comment/{}/'.format(comment.id))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_retrieve_comment_community_event_authenticated(self):
        ''' Test retrieve comment on community events while authenticated '''
        self.client.login(username='user_01', password='12345678')

        self._test_retrieve_comment_community_event(
            is_publicly_visible=True, created_under_id=self.club_public.id, allows_retrieve=True
        )
        self._test_retrieve_comment_community_event(
            is_publicly_visible=True, created_under_id=self.club_private.id, allows_retrieve=True
        )
        self._test_retrieve_comment_community_event(
            is_publicly_visible=False, created_under_id=self.club_public.id, allows_retrieve=True
        )
        self._test_retrieve_comment_community_event(
            is_publicly_visible=False, created_under_id=self.club_private.id, allows_retrieve=True
        )

        self.client.logout()

    def test_retrieve_comment_community_event_unauthenticated(self):
        ''' Test retrieve comment on community events while unauthenticated '''
        self._test_retrieve_comment_community_event(
            is_publicly_visible=True, created_under_id=self.club_public.id, allows_retrieve=True
        )
        self._test_retrieve_comment_community_event(
            is_publicly_visible=True, created_under_id=self.club_private.id, allows_retrieve=False
        )
        self._test_retrieve_comment_community_event(
            is_publicly_visible=False, created_under_id=self.club_public.id, allows_retrieve=False
        )
        self._test_retrieve_comment_community_event(
            is_publicly_visible=False, created_under_id=self.club_private.id, allows_retrieve=False
        )

    def _test_retrieve_comment_community_event(self, is_publicly_visible=True, created_under_id=int(),
                                               allows_retrieve=True):
        ''' Test retrieve comment on community events '''
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
        response = self.client.get('/api/asset/comment/{}/'.format(comment.id))

        if allows_retrieve:
            self.assertEqual(response.status_code, status.HTTP_200_OK)
        else:
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        comment.delete()

    def test_create_comment_event_authenticated(self):
        ''' Test create comment on events while authenticated '''
        self.client.login(username='user_01', password='12345678')

        response = self.client.post('/api/asset/comment/', {
            'text': 'Greetings!',
            'written_by': 'Guest',
            'event': self.event_public.id
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        response = self.client.post('/api/asset/comment/', {
            'text': 'Greetings!',
            'written_by': 'Guest',
            'event': self.event_private.id
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.client.logout()

    def test_create_comment_event_unauthenticated(self):
        ''' Test create comment on events while unauthenticated '''
        response = self.client.post('/api/asset/comment/', {
            'text': 'Greetings!',
            'written_by': 'Guest',
            'event': self.event_public.id
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        response = self.client.post('/api/asset/comment/', {
            'text': 'Greetings!',
            'written_by': 'Guest',
            'event': self.event_private.id
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_comment_community_event_authenticated_member(self):
        ''' Test create comment on community events while authenticated and a member '''
        self.client.login(username='user_01', password='12345678')

        self._test_create_comment_community_event(
            is_publicly_visible=True, created_under_id=self.club_public.id, allows_outside_participators=True,
            add_member='user_01', allows_retrieve=True
        )
        self._test_create_comment_community_event(
            is_publicly_visible=True, created_under_id=self.club_public.id, allows_outside_participators=False,
            add_member='user_01', allows_retrieve=True
        )
        self._test_create_comment_community_event(
            is_publicly_visible=True, created_under_id=self.club_private.id, allows_outside_participators=True,
            add_member='user_01', allows_retrieve=True
        )
        self._test_create_comment_community_event(
            is_publicly_visible=True, created_under_id=self.club_private.id, allows_outside_participators=False,
            add_member='user_01', allows_retrieve=True
        )
        self._test_create_comment_community_event(
            is_publicly_visible=False, created_under_id=self.club_public.id, allows_outside_participators=True,
            add_member='user_01', allows_retrieve=True
        )
        self._test_create_comment_community_event(
            is_publicly_visible=False, created_under_id=self.club_public.id, allows_outside_participators=False,
            add_member='user_01', allows_retrieve=True
        )
        self._test_create_comment_community_event(
            is_publicly_visible=False, created_under_id=self.club_private.id, allows_outside_participators=True,
            add_member='user_01', allows_retrieve=True
        )
        self._test_create_comment_community_event(
            is_publicly_visible=False, created_under_id=self.club_private.id, allows_outside_participators=False,
            add_member='user_01', allows_retrieve=True
        )

        self.client.logout()

    def test_create_comment_community_event_authenticated_non_member(self):
        ''' Test create comment on community events while authenticated and a member '''
        self.client.login(username='user_01', password='12345678')

        self._test_create_comment_community_event(
            is_publicly_visible=True, created_under_id=self.club_public.id, allows_outside_participators=True,
            allows_retrieve=True
        )
        self._test_create_comment_community_event(
            is_publicly_visible=True, created_under_id=self.club_public.id, allows_outside_participators=False,
            allows_retrieve=False
        )
        self._test_create_comment_community_event(
            is_publicly_visible=True, created_under_id=self.club_private.id, allows_outside_participators=True,
            allows_retrieve=True
        )
        self._test_create_comment_community_event(
            is_publicly_visible=True, created_under_id=self.club_private.id, allows_outside_participators=False,
            allows_retrieve=False
        )
        self._test_create_comment_community_event(
            is_publicly_visible=False, created_under_id=self.club_public.id, allows_outside_participators=True,
            allows_retrieve=True
        )
        self._test_create_comment_community_event(
            is_publicly_visible=False, created_under_id=self.club_public.id, allows_outside_participators=False,
            allows_retrieve=False
        )
        self._test_create_comment_community_event(
            is_publicly_visible=False, created_under_id=self.club_private.id, allows_outside_participators=True,
            allows_retrieve=True
        )
        self._test_create_comment_community_event(
            is_publicly_visible=False, created_under_id=self.club_private.id, allows_outside_participators=False,
            allows_retrieve=False
        )

        self.client.logout()

    def test_create_comment_community_event_unauthenticated(self):
        ''' Test create comment on community events while unauthenticated '''
        self._test_create_comment_community_event(
            is_publicly_visible=True, created_under_id=self.club_public.id, allows_outside_participators=True,
            allows_retrieve=True
        )
        self._test_create_comment_community_event(
            is_publicly_visible=True, created_under_id=self.club_public.id, allows_outside_participators=False,
            allows_retrieve=False
        )
        self._test_create_comment_community_event(
            is_publicly_visible=True, created_under_id=self.club_private.id, allows_outside_participators=True,
            allows_retrieve=False
        )
        self._test_create_comment_community_event(
            is_publicly_visible=True, created_under_id=self.club_private.id, allows_outside_participators=False,
            allows_retrieve=False
        )
        self._test_create_comment_community_event(
            is_publicly_visible=False, created_under_id=self.club_public.id, allows_outside_participators=True,
            allows_retrieve=False
        )
        self._test_create_comment_community_event(
            is_publicly_visible=False, created_under_id=self.club_public.id, allows_outside_participators=False,
            allows_retrieve=False
        )
        self._test_create_comment_community_event(
            is_publicly_visible=False, created_under_id=self.club_private.id, allows_outside_participators=True,
            allows_retrieve=False
        )
        self._test_create_comment_community_event(
            is_publicly_visible=False, created_under_id=self.club_private.id, allows_outside_participators=False,
            allows_retrieve=False
        )

    def _test_create_comment_community_event(self, is_publicly_visible=True, created_under_id=int(),
                                             allows_outside_participators=True, add_member=None, allows_retrieve=True):
        ''' Test create comment on community events '''
        community_event = CommunityEvent.objects.create(
            name_th='กิจกรรมชุมนุมทดสอบความคิดเห็น พิเศษ - {}'.format(get_random_string(length=16)),
            name_en='Comment Testing Club Event (Special) - {}'.format(get_random_string(length=16)),
            is_approved=True, location='L207 IT KMITL',
            start_date=datetime.date(2020, 12, 1), end_date=datetime.date(2020, 12, 2),
            start_time=datetime.time(9, 0, 0), end_time=datetime.time(17, 0, 0),
            is_publicly_visible=is_publicly_visible, created_under_id=created_under_id,
            allows_outside_participators=allows_outside_participators
        )

        if isinstance(add_member, str):
            Membership.objects.create(
                user_id=get_user_model().objects.get(username=add_member).id, community_id=community_event.id
            )

        response = self.client.post('/api/asset/comment/', {
            'text': 'Greetings!',
            'written_by': 'Guest',
            'event': community_event.id
        })

        if allows_retrieve:
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        else:
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_comment(self):
        ''' Test update comment '''
        self.client.login(username='user_01', password='12345678')

        comment = Comment.objects.create(text='Greetings!', written_by='Guest', event_id=self.event_public.id)
        response = self.client.put('/api/asset/comment/{}/'.format(comment.id), {
            'text': 'Hello!'
        })
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(Comment.objects.get(pk=comment.id).text, 'Greetings!')

        comment = Comment.objects.create(text='Greetings!', written_by='Guest', event_id=self.event_public.id)
        response = self.client.patch('/api/asset/comment/{}/'.format(comment.id), {
            'text': 'Hello!'
        })
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(Comment.objects.get(pk=comment.id).text, 'Greetings!')

        self.client.logout()

    def test_delete_comment_as_leader(self):
        ''' Test delete comments as leader '''
        self._test_delete_comment(username='user_01', created_by_id=self.user_01.id, allows_delete=True)
        self._test_delete_comment(username='user_01', created_by_id=self.user_02.id, allows_delete=True)
        self._test_delete_comment(username='user_01', created_by_id=self.user_03.id, allows_delete=True)
        self._test_delete_comment(username='user_01', created_by_id=self.user_04.id, allows_delete=True)
        self._test_delete_comment(username='user_01', created_by_id=self.user_05.id, allows_delete=True)
        self._test_delete_comment(username='user_01', created_by_id=None, allows_delete=True)

    def test_delete_comment_as_deputy_leader(self):
        ''' Test delete comments as deputy leader '''
        self._test_delete_comment(username='user_02', created_by_id=self.user_01.id, allows_delete=True)
        self._test_delete_comment(username='user_02', created_by_id=self.user_02.id, allows_delete=True)
        self._test_delete_comment(username='user_02', created_by_id=self.user_03.id, allows_delete=True)
        self._test_delete_comment(username='user_02', created_by_id=self.user_04.id, allows_delete=True)
        self._test_delete_comment(username='user_02', created_by_id=self.user_05.id, allows_delete=True)
        self._test_delete_comment(username='user_02', created_by_id=None, allows_delete=True)

    def test_delete_comment_as_staff(self):
        ''' Test delete comments as staff '''
        self._test_delete_comment(username='user_03', created_by_id=self.user_01.id, allows_delete=False)
        self._test_delete_comment(username='user_03', created_by_id=self.user_02.id, allows_delete=False)
        self._test_delete_comment(username='user_03', created_by_id=self.user_03.id, allows_delete=True)
        self._test_delete_comment(username='user_03', created_by_id=self.user_04.id, allows_delete=False)
        self._test_delete_comment(username='user_03', created_by_id=self.user_05.id, allows_delete=False)
        self._test_delete_comment(username='user_03', created_by_id=None, allows_delete=False)

    def test_delete_comment_as_member(self):
        ''' Test delete comments as member '''
        self._test_delete_comment(username='user_04', created_by_id=self.user_01.id, allows_delete=False)
        self._test_delete_comment(username='user_04', created_by_id=self.user_02.id, allows_delete=False)
        self._test_delete_comment(username='user_04', created_by_id=self.user_03.id, allows_delete=False)
        self._test_delete_comment(username='user_04', created_by_id=self.user_04.id, allows_delete=True)
        self._test_delete_comment(username='user_04', created_by_id=self.user_05.id, allows_delete=False)
        self._test_delete_comment(username='user_04', created_by_id=None, allows_delete=False)

    def test_delete_comment_as_non_member(self):
        ''' Test delete comments as non-member '''
        self._test_delete_comment(username='user_05', created_by_id=self.user_01.id, allows_delete=False)
        self._test_delete_comment(username='user_05', created_by_id=self.user_02.id, allows_delete=False)
        self._test_delete_comment(username='user_05', created_by_id=self.user_03.id, allows_delete=False)
        self._test_delete_comment(username='user_05', created_by_id=self.user_04.id, allows_delete=False)
        self._test_delete_comment(username='user_05', created_by_id=self.user_05.id, allows_delete=True)
        self._test_delete_comment(username='user_05', created_by_id=None, allows_delete=False)

    def test_delete_comment_unauthenticated(self):
        ''' Test delete comment while unauthenticated '''
        self._test_delete_comment(created_by_id=self.user_01.id, allows_delete=False)
        self._test_delete_comment(created_by_id=self.user_02.id, allows_delete=False)
        self._test_delete_comment(created_by_id=self.user_03.id, allows_delete=False)
        self._test_delete_comment(created_by_id=self.user_04.id, allows_delete=False)
        self._test_delete_comment(created_by_id=self.user_05.id, allows_delete=False)
        self._test_delete_comment(created_by_id=None, allows_delete=False)

    def _test_delete_comment(self, username=str(), created_by_id=None, allows_delete=True):
        ''' Test delete comment '''
        if username.strip() != str():
            self.client.login(username=username, password='12345678')

        comment = Comment.objects.create(
            text='Greetings!', written_by='It\'s me', event_id=self.event_public.id, created_by_id=created_by_id
        )
        response = self.client.delete('/api/asset/comment/{}/'.format(comment.id))

        if allows_delete:
            self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        else:
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        if username.strip() != str():
            self.client.logout()
