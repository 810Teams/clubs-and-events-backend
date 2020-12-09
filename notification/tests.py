'''
    Notification Application Tests
    notification/tests.py
    @author Teerapat Kraisrisirikul (810Teams)
'''

from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from community.models import Club
from membership.models import Membership
from notification.models import RequestNotification, AnnouncementNotification, CommunityEventNotification, \
    EventNotification

import datetime

from user.models import StudentCommitteeAuthority


class NotificationAPITest(APITestCase):
    ''' Notification API test '''
    def setUp(self):
        ''' Set up '''
        self.user_01 = get_user_model().objects.create_user(username='user_01', password='12345678')
        self.user_02 = get_user_model().objects.create_user(username='user_02', password='12345678')
        self.user_03 = get_user_model().objects.create_user(username='user_03', password='12345678')
        self.user_04 = get_user_model().objects.create_user(username='user_04', password='12345678')
        self.user_05 = get_user_model().objects.create_user(username='user_05', password='12345678')
        self.club = Club.objects.create(
            name_th='ชุมนุมนอน', name_en='Sleeping Club', is_accepting_requests=True, is_official=True
        )

        Membership.objects.create(community_id=self.club.id, user_id=self.user_01.id, position=3)
        Membership.objects.create(community_id=self.club.id, user_id=self.user_02.id, position=2)
        Membership.objects.create(community_id=self.club.id, user_id=self.user_03.id, position=1)
        Membership.objects.create(community_id=self.club.id, user_id=self.user_04.id, position=0)
        StudentCommitteeAuthority.objects.create(
            user_id=self.user_01.id,
            start_date=datetime.date(1970, 1, 1),
            end_date=datetime.date(2099, 12, 31)
        )

        self.club_members = 4
        self.non_club_members = 1

    def test_request_notification(self):
        ''' Test request notification '''
        self.client.login(username='user_05', password='12345678')

        self.assertEqual(len(RequestNotification.objects.all()), 0)
        self.client.post('/api/membership/request/', {
            'community': self.club.id
        })
        self.assertEqual(len(RequestNotification.objects.all()), self.club_members - 1)

        self.client.logout()

    def test_announcement_notification(self):
        ''' Test announcement notification '''
        self.client.login(username='user_01', password='12345678')

        self.assertEqual(len(AnnouncementNotification.objects.all()), 0)
        self.client.post('/api/asset/announcement/', {
            'community': self.club.id,
            'text': 'Test announcement notification'
        })
        self.assertEqual(len(AnnouncementNotification.objects.all()), self.club_members - 1)

        self.client.logout()

    def test_community_event_notification_future(self):
        ''' Test community event, future community event '''
        self.client.login(username='user_01', password='12345678')

        self.assertEqual(len(CommunityEventNotification.objects.all()), 0)
        self.client.post('/api/community/event/community/', {
            'name_th': 'นอนกันเถอะ 1',
            'name_en': 'Let\'s Sleep! 1',
            'location': 'Anywhere',
            'start_date': datetime.date(2099, 1, 1),
            'end_date': datetime.date(2099, 1, 1),
            'start_time': datetime.time(12, 0, 0),
            'end_time': datetime.time(12, 30, 0),
            'created_under': self.club.id
        })
        self.assertEqual(len(CommunityEventNotification.objects.all()), self.club_members - 1)

        self.client.logout()

    def test_community_event_notification_past(self):
        ''' Test community event, past community event '''
        self.client.login(username='user_01', password='12345678')

        self.assertEqual(len(CommunityEventNotification.objects.all()), 0)
        self.client.post('/api/community/event/community/', {
            'name_th': 'นอนกันเถอะ 2',
            'name_en': 'Let\'s Sleep! 2',
            'location': 'Anywhere',
            'start_date': datetime.date(1970, 1, 1),
            'end_date': datetime.date(1970, 1, 1),
            'start_time': datetime.time(12, 0, 0),
            'end_time': datetime.time(12, 30, 0),
            'created_under': self.club.id
        })
        self.assertEqual(len(CommunityEventNotification.objects.all()), 0)

        self.client.logout()

    def test_event_notification_future(self):
        ''' Test event notification, future event '''
        self.client.login(username='user_01', password='12345678')

        self.assertEqual(len(EventNotification.objects.all()), 0)
        response = self.client.post('/api/community/event/', {
            'name_th': 'ไอทีแคมป์ 1',
            'name_en': 'IT CAMP 1',
            'location': 'IT KMITL',
            'start_date': datetime.date(2099, 1, 1),
            'end_date': datetime.date(2099, 1, 1),
            'start_time': datetime.time(12, 0, 0),
            'end_time': datetime.time(12, 30, 0)
        })
        self.assertEqual(len(EventNotification.objects.all()), 0)
        response = self.client.post('/api/membership/approval-request/', {
            'community': response.data['id'],
        })
        self.client.patch('/api/membership/approval-request/{}/'.format(response.data['id']), {
            'status': 'A'
        })
        self.assertEqual(len(EventNotification.objects.all()), self.club_members + self.non_club_members)

        self.client.logout()

    def test_event_notification_past(self):
        ''' Test event notification, past event '''
        self.client.login(username='user_01', password='12345678')

        self.assertEqual(len(EventNotification.objects.all()), 0)
        response = self.client.post('/api/community/event/', {
            'name_th': 'ไอทีแคมป์ 2',
            'name_en': 'IT CAMP 2',
            'location': 'IT KMITL',
            'start_date': datetime.date(1970, 1, 1),
            'end_date': datetime.date(1970, 1, 1),
            'start_time': datetime.time(12, 0, 0),
            'end_time': datetime.time(12, 30, 0)
        })
        self.assertEqual(len(EventNotification.objects.all()), 0)
        response = self.client.post('/api/membership/approval-request/', {
            'community': response.data['id'],
        })
        self.client.patch('/api/membership/approval-request/{}/'.format(response.data['id']), {
            'status': 'A'
        })
        self.assertEqual(len(EventNotification.objects.all()), 0)

        self.client.logout()
