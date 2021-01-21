'''
    Miscellaneous Application Tests
    misc/tests.py
    @author Teerapat Kraisrisirikul (810Teams)
'''

from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from clubs_and_events.settings import VOTE_LIMIT_PER_EVENT
from community.models import Event
from membership.models import Membership
from misc.models import FAQ, Vote

import datetime


class FAQAPITest(APITestCase):
    ''' Frequently asked question (FAQ) API test '''
    def setUp(self):
        ''' Set up '''
        self.user_01 = get_user_model().objects.create_user(username='user_01', password='12345678', name='User One')

    def test_list_faq_authenticated(self):
        ''' Test list FAQ while authenticated '''
        self.client.login(username='user_01', password='12345678')

        FAQ.objects.create(question='Why do I feel not working?', answer='It\'s simple. You\'re just lazy.')
        response = self.client.get('/api/misc/faq/')
        self.assertEqual(len(response.data), 1)

        self.client.logout()

    def test_list_faq_unauthenticated(self):
        ''' Test list FAQ while unauthenticated '''
        FAQ.objects.create(question='Why do I feel not working?', answer='It\'s simple. You\'re just lazy.')
        response = self.client.get('/api/misc/faq/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_retrieve_faq_authenticated(self):
        ''' Test retrieve FAQ while authenticated '''
        self.client.login(username='user_01', password='12345678')

        faq = FAQ.objects.create(question='Why do I feel not working?', answer='It\'s simple. You\'re just lazy.')
        response = self.client.get('/api/misc/faq/{}/'.format(faq.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.client.logout()

    def test_retrieve_faq_unauthenticated(self):
        ''' Test retrieve FAQ while unauthenticated '''
        faq = FAQ.objects.create(question='Why do I feel not working?', answer='It\'s simple. You\'re just lazy.')
        response = self.client.get('/api/misc/faq/{}/'.format(faq.id))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_faq(self):
        ''' Test create FAQ '''
        self.client.login(username='user_01', password='12345678')

        response = self.client.post('/api/misc/faq/', {
            'question': 'Why do I feel not working?',
            'answer': 'It\'s simple. You\'re just lazy.'
        })
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        self.client.logout()

    def test_update_faq(self):
        ''' Test update FAQ '''
        self.client.login(username='user_01', password='12345678')

        faq = FAQ.objects.create(question='Why do I feel not working?', answer='It\'s simple. You\'re just lazy.')
        response = self.client.put('/api/misc/faq/{}/'.format(faq.id), {
            'answer': 'There are various reasons that may be causing this.'
        })
        self.assertEqual(FAQ.objects.get(pk=faq.id).answer, 'It\'s simple. You\'re just lazy.')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        faq = FAQ.objects.create(question='Why do I feel sleepy?', answer='It\'s simple. You were up all night gaming.')
        response = self.client.patch('/api/misc/faq/{}/'.format(faq.id), {
            'answer': 'You need more caffeine.'
        })
        self.assertEqual(FAQ.objects.get(pk=faq.id).answer, 'It\'s simple. You were up all night gaming.')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        self.client.logout()

    def test_delete_faq(self):
        ''' Test delete FAQ '''
        self.client.login(username='user_01', password='12345678')

        faq = FAQ.objects.create(question='Why do I feel not working?', answer='It\'s simple. You\'re just lazy.')
        response = self.client.delete('/api/misc/faq/{}/'.format(faq.id))
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        self.client.logout()


class VoteAPITest(APITestCase):
    ''' Vote API test '''
    def setUp(self):
        ''' Set up '''
        self.user_01 = get_user_model().objects.create_user(username='user_01', password='12345678', name='User One')
        self.user_02 = get_user_model().objects.create_user(username='user_02', password='12345678', name='User Two')
        self.user_03 = get_user_model().objects.create_user(username='user_03', password='12345678', name='User Three')
        self.user_04 = get_user_model().objects.create_user(username='user_04', password='12345678', name='User Four')
        self.user_05 = get_user_model().objects.create_user(username='user_05', password='12345678', name='User Five')

        self.event_past = Event.objects.create(
            name_th='กิจกรรมทดสอบโหวต (อดีต)',
            name_en='Vote Testing Event (Past)',
            is_approved=True,
            location='L207 IT KMITL',
            start_date=datetime.date(1970, 1, 1),
            end_date=datetime.date(1970, 1, 2),
            start_time=datetime.time(9, 0, 0),
            end_time=datetime.time(17, 0, 0)
        )
        self.event_on_going = Event.objects.create(
            name_th='กิจกรรมทดสอบโหวต (กำลังดำเนินอยู่)',
            name_en='Vote Testing Event (On-going)',
            is_approved=True,
            location='L207 IT KMITL',
            start_date=datetime.date(1970, 1, 1),
            end_date=datetime.date(2099, 12, 31),
            start_time=datetime.time(9, 0, 0),
            end_time=datetime.time(17, 0, 0)
        )
        self.event_future = Event.objects.create(
            name_th='กิจกรรมทดสอบโหวต (อนาคต)',
            name_en='Vote Testing Event (Future)',
            is_approved=True,
            location='L207 IT KMITL',
            start_date=datetime.date(2099, 12, 30),
            end_date=datetime.date(2099, 12, 31),
            start_time=datetime.time(9, 0, 0),
            end_time=datetime.time(17, 0, 0)
        )
        self.event_unapproved = Event.objects.create(
            name_th='กิจกรรมทดสอบโหวต (ยังไม่อนุมัติ)',
            name_en='Vote Testing Event (Unapproved)',
            is_approved=False,
            location='L207 IT KMITL',
            start_date=datetime.date(1970, 1, 1),
            end_date=datetime.date(1970, 1, 2),
            start_time=datetime.time(9, 0, 0),
            end_time=datetime.time(17, 0, 0)
        )

        self.mp1 = Membership.objects.create(community_id=self.event_past.id, user_id=self.user_01.id, position=3)
        self.mp2 = Membership.objects.create(community_id=self.event_past.id, user_id=self.user_02.id, position=2)
        self.mp3 = Membership.objects.create(community_id=self.event_past.id, user_id=self.user_03.id, position=1)
        self.mp4 = Membership.objects.create(community_id=self.event_past.id, user_id=self.user_04.id, position=0)

        self.mo1 = Membership.objects.create(community_id=self.event_on_going.id, user_id=self.user_01.id, position=3)
        self.mo2 = Membership.objects.create(community_id=self.event_on_going.id, user_id=self.user_02.id, position=2)
        self.mo3 = Membership.objects.create(community_id=self.event_on_going.id, user_id=self.user_03.id, position=1)
        self.mo4 = Membership.objects.create(community_id=self.event_on_going.id, user_id=self.user_04.id, position=0)

        self.mf1 = Membership.objects.create(community_id=self.event_future.id, user_id=self.user_01.id, position=3)
        self.mf2 = Membership.objects.create(community_id=self.event_future.id, user_id=self.user_02.id, position=2)
        self.mf3 = Membership.objects.create(community_id=self.event_future.id, user_id=self.user_03.id, position=1)
        self.mf4 = Membership.objects.create(community_id=self.event_future.id, user_id=self.user_04.id, position=0)

        self.mu1 = Membership.objects.create(community_id=self.event_unapproved.id, user_id=self.user_01.id, position=3)
        self.mu2 = Membership.objects.create(community_id=self.event_unapproved.id, user_id=self.user_02.id, position=2)
        self.mu3 = Membership.objects.create(community_id=self.event_unapproved.id, user_id=self.user_03.id, position=1)
        self.mu4 = Membership.objects.create(community_id=self.event_unapproved.id, user_id=self.user_04.id, position=0)

    def test_list_vote_unauthenticated(self):
        ''' Test list vote while unauthenticated '''
        Vote.objects.create(voted_for_id=self.mp1.id, voted_by_id=self.user_02.id)
        Vote.objects.create(voted_for_id=self.mp2.id, voted_by_id=self.user_03.id)
        Vote.objects.create(voted_for_id=self.mp2.id, voted_by_id=self.user_03.id)
        Vote.objects.create(voted_for_id=self.mp3.id, voted_by_id=self.user_04.id)

        response = self.client.get('/api/misc/vote/')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_vote_authenticated(self):
        ''' Test list vote while authenticated '''
        self.client.login(username='user_01', password='12345678')

        Vote.objects.create(voted_for_id=self.mp1.id, voted_by_id=self.user_02.id)
        Vote.objects.create(voted_for_id=self.mp2.id, voted_by_id=self.user_03.id)
        Vote.objects.create(voted_for_id=self.mp2.id, voted_by_id=self.user_03.id)
        Vote.objects.create(voted_for_id=self.mp3.id, voted_by_id=self.user_04.id)

        response = self.client.get('/api/misc/vote/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 4)

        self.client.logout()

    def test_retrieve_vote_unauthenticated(self):
        ''' Test retrieve vote while unauthenticated '''
        vote = Vote.objects.create(voted_for_id=self.mp1.id, voted_by_id=self.user_03.id)
        response = self.client.get('/api/misc/vote/{}/'.format(vote.id))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        vote = Vote.objects.create(voted_for_id=self.mp2.id, voted_by_id=self.user_04.id)
        response = self.client.get('/api/misc/vote/{}/'.format(vote.id))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_retrieve_vote_authenticated(self):
        ''' Test retrieve vote while unauthenticated '''
        self.client.login(username='user_01', password='12345678')

        vote = Vote.objects.create(voted_for_id=self.mp1.id, voted_by_id=self.user_03.id)
        response = self.client.get('/api/misc/vote/{}/'.format(vote.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        vote = Vote.objects.create(voted_for_id=self.mp2.id, voted_by_id=self.user_04.id)
        response = self.client.get('/api/misc/vote/{}/'.format(vote.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.client.logout()

    def test_create_vote_in_past_event(self):
        ''' Test create vote in past event '''
        self._test_create_vote_in(voted_for_id=self.mp1.id, allows_create=True)

    def test_create_vote_in_on_going_event(self):
        ''' Test create vote in on-going event '''
        self._test_create_vote_in(voted_for_id=self.mo1.id, allows_create=False)

    def test_create_vote_in_future_event(self):
        ''' Test create vote in future event '''
        self._test_create_vote_in(voted_for_id=self.mf1.id, allows_create=False)

    def test_create_vote_in_unapproved_event(self):
        ''' Test create vote in unapproved event '''
        self._test_create_vote_in(voted_for_id=self.mu1.id, allows_create=False)

    def _test_create_vote_in(self, voted_for_id=int(), allows_create=True):
        ''' Test create vote in different events '''
        self._test_create_vote(username='user_01', voted_for_id=voted_for_id, allows_create=False)
        self._test_create_vote(username='user_02', voted_for_id=voted_for_id, allows_create=allows_create)
        self._test_create_vote(username='user_03', voted_for_id=voted_for_id, allows_create=allows_create)
        self._test_create_vote(username='user_04', voted_for_id=voted_for_id, allows_create=allows_create)
        self._test_create_vote(username='user_05', voted_for_id=voted_for_id, allows_create=False)
        self._test_create_vote(username=str(), voted_for_id=voted_for_id, allows_create=False)

    def test_create_vote_duplicate(self):
        ''' Test create duplicate votes '''
        self._test_create_vote(username='user_01', voted_for_id=self.mp2.id, allows_create=True)
        self._test_create_vote(username='user_01', voted_for_id=self.mp2.id, allows_create=False)
        self._test_create_vote(username='user_01', voted_for_id=self.mp3.id, allows_create=True)
        self._test_create_vote(username='user_01', voted_for_id=self.mp3.id, allows_create=False)

        self._test_create_vote(username='user_02', voted_for_id=self.mp1.id, allows_create=True)
        self._test_create_vote(username='user_02', voted_for_id=self.mp1.id, allows_create=False)
        self._test_create_vote(username='user_02', voted_for_id=self.mp3.id, allows_create=True)
        self._test_create_vote(username='user_02', voted_for_id=self.mp3.id, allows_create=False)

    def test_create_vote_exceed(self):
        ''' Test create vote exceeding the limit '''
        for i in range(VOTE_LIMIT_PER_EVENT + 1):
            user = get_user_model().objects.create_user(
                username='user_temp_{:02d}'.format(i + 1), password='12345678', name='User Temp {:02d}'.format(i + 1)
            )
            membership = Membership.objects.create(community_id=self.event_past.id, user_id=user.id, position=1)

            if i < VOTE_LIMIT_PER_EVENT:
                self._test_create_vote(username='user_01', voted_for_id=membership.id, allows_create=True)
            else:
                self._test_create_vote(username='user_01', voted_for_id=membership.id, allows_create=False)

    def _test_create_vote(self, username=str(), voted_for_id=int(), allows_create=True):
        ''' Test create vote '''
        if isinstance(username, str) and username.strip() != str():
            self.client.login(username=username, password='12345678')

        response = self.client.post('/api/misc/vote/', {
            'comment': 'Amazing performance!',
            'voted_for': voted_for_id
        })

        if allows_create:
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        else:
            self.assertIn(response.status_code, (status.HTTP_400_BAD_REQUEST, status.HTTP_403_FORBIDDEN))

        if isinstance(username, str) and username.strip() != str():
            self.client.logout()

    def test_update_vote_as_voter(self):
        ''' Test update vote as voter '''
        self.client.login(username='user_01', password='12345678')

        vote = Vote.objects.create(comment='Astonishing!', voted_for_id=self.mp2.id, voted_by_id=self.user_01.id)

        response = self.client.put('/api/misc/vote/{}/'.format(vote.id), {
            'comment': 'Amazing!'
        })
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(Vote.objects.get(pk=vote.id).comment, 'Astonishing!')

        response = self.client.patch('/api/misc/vote/{}/'.format(vote.id), {
            'comment': 'Amazing!'
        })
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(Vote.objects.get(pk=vote.id).comment, 'Astonishing!')

        self.client.logout()

    def test_update_vote_as_vote_receiver(self):
        ''' Test update vote as vote receiver '''
        self.client.login(username='user_02', password='12345678')

        vote = Vote.objects.create(comment='Astonishing!', voted_for_id=self.mp2.id, voted_by_id=self.user_01.id)

        response = self.client.put('/api/misc/vote/{}/'.format(vote.id), {
            'comment': 'Amazing!'
        })
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(Vote.objects.get(pk=vote.id).comment, 'Astonishing!')

        response = self.client.patch('/api/misc/vote/{}/'.format(vote.id), {
            'comment': 'Amazing!'
        })
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(Vote.objects.get(pk=vote.id).comment, 'Astonishing!')

        self.client.logout()

    def test_delete_vote_as_voter(self):
        ''' Test delete vote as voter '''
        self.client.login(username='user_01', password='12345678')

        vote = Vote.objects.create(comment='Astonishing!', voted_for_id=self.mp2.id, voted_by_id=self.user_01.id)
        response = self.client.delete('/api/misc/vote/{}/'.format(vote.id))
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        self.client.logout()

    def test_delete_vote_as_vote_receiver(self):
        ''' Test delete vote as vote receiver '''
        self.client.login(username='user_02', password='12345678')

        vote = Vote.objects.create(comment='Astonishing!', voted_for_id=self.mp2.id, voted_by_id=self.user_01.id)
        response = self.client.delete('/api/misc/vote/{}/'.format(vote.id))
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        self.client.logout()
