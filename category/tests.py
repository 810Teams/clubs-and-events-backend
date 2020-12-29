'''
    Category Application Tests
    category/tests.py
    @author Teerapat Kraisrisirikul (810Teams)
'''

from rest_framework import status
from rest_framework.test import APITestCase

from category.models import ClubType, EventType, EventSeries


class ClubTypeAPITest(APITestCase):
    ''' Club type API test '''
    def setUp(self):
        ''' Set up '''
        self.academic = ClubType.objects.create(title_th='วิชาการ', title_en='Academic')
        self.arts = ClubType.objects.create(title_th='ศิลปะ', title_en='Arts')
        self.culture = ClubType.objects.create(title_th='วัฒนธรรมและภาษา', title_en='Culture and Language')
        self.entertainment = ClubType.objects.create(title_th='บันเทิง', title_en='Entertainment')
        self.sports = ClubType.objects.create(title_th='กีฬา', title_en='Sports')
        self.travel = ClubType.objects.create(title_th='ท่องเที่ยว', title_en='Travel')

    def test_list_club_type(self):
        ''' Test list club type '''
        response = self.client.get('/api/category/club-type/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 6)

    def test_retrieve_club_type(self):
        ''' Test retrieve club type '''
        response = self.client.get('/api/category/club-type/{}/'.format(self.academic.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('title_th', response.data.keys())
        self.assertIn('title_en', response.data.keys())

    def test_create_club_type(self):
        ''' Test create club type '''
        response = self.client.post('/api/category/club-type/', {
            'title_th': 'ไม่ได้ตั้งชื่อ',
            'title_en': 'Unnamed'
        })
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_club_type(self):
        ''' Test update club type '''
        response = self.client.put('/api/category/club-type/{}/'.format(self.academic.id), {
            'title_th': 'ไม่ได้ตั้งชื่อ',
            'title_en': 'Unnamed'
        })
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.patch('/api/category/club-type/{}/'.format(self.academic.id), {
            'title_th': 'ไม่ได้ตั้งชื่อ',
            'title_en': 'Unnamed'
        })
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_delete_club_type(self):
        ''' Test delete club type '''
        response = self.client.delete('/api/category/club-type/{}/'.format(self.academic.id))
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)


class EventTypeAPITest(APITestCase):
    ''' Event type API test '''
    def setUp(self):
        ''' Set up '''
        self.academic = EventType.objects.create(title_th='วิชาการ', title_en='Academic')
        self.arts = EventType.objects.create(title_th='ศิลปะ', title_en='Arts')
        self.culture = EventType.objects.create(title_th='วัฒนธรรมและภาษา', title_en='Culture and Language')
        self.entertainment = EventType.objects.create(title_th='บันเทิง', title_en='Entertainment')
        self.sports = EventType.objects.create(title_th='กีฬา', title_en='Sports')
        self.travel = EventType.objects.create(title_th='ท่องเที่ยว', title_en='Travel')

    def test_list_event_type(self):
        ''' Test list event type '''
        response = self.client.get('/api/category/event-type/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 6)

    def test_retrieve_event_type(self):
        ''' Test retrieve event type '''
        response = self.client.get('/api/category/event-type/{}/'.format(self.academic.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('title_th', response.data.keys())
        self.assertIn('title_en', response.data.keys())

    def test_create_event_type(self):
        ''' Test create event type '''
        response = self.client.post('/api/category/event-type/', {
            'title_th': 'ไม่ได้ตั้งชื่อ',
            'title_en': 'Unnamed'
        })
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_event_type(self):
        ''' Test update event type '''
        response = self.client.put('/api/category/event-type/{}/'.format(self.academic.id), {
            'title_th': 'ไม่ได้ตั้งชื่อ',
            'title_en': 'Unnamed'
        })
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.patch('/api/category/event-type/{}/'.format(self.academic.id), {
            'title_th': 'ไม่ได้ตั้งชื่อ',
            'title_en': 'Unnamed'
        })
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_delete_event_type(self):
        ''' Test delete event type '''
        response = self.client.delete('/api/category/event-type/{}/'.format(self.academic.id))
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)


class EventSeriesAPITest(APITestCase):
    ''' Event series API test '''
    def setUp(self):
        ''' Set up '''
        self.to_be_it = EventSeries.objects.create(title_th='ทูบีไอที ติวน้องสอบตรงไอทีลาดกระบัง', title_en='ToBeIT@KMITL')
        self.oph = EventSeries.objects.create(title_th='เปิดบ้านไอทีลาดกระบัง', title_en='ITLadkrabang OpenHouse')
        self.pre_pro = EventSeries.objects.create(title_th='พรีโปรแกรมมิ่ง', title_en='Pre-Programming')

    def test_list_event_series(self):
        ''' Test list event series '''
        response = self.client.get('/api/category/event-series/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)

    def test_retrieve_event_series(self):
        ''' Test retrieve event series '''
        response = self.client.get('/api/category/event-series/{}/'.format(self.to_be_it.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('title_th', response.data.keys())
        self.assertIn('title_en', response.data.keys())

    def test_create_event_series(self):
        ''' Test create event series '''
        response = self.client.post('/api/category/event-series/', {
            'title_th': 'ไม่ได้ตั้งชื่อ',
            'title_en': 'Unnamed'
        })
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_event_series(self):
        ''' Test update event series '''
        response = self.client.put('/api/category/event-series/{}/'.format(self.to_be_it.id), {
            'title_th': 'ไม่ได้ตั้งชื่อ',
            'title_en': 'Unnamed'
        })
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.patch('/api/category/event-series/{}/'.format(self.to_be_it.id), {
            'title_th': 'ไม่ได้ตั้งชื่อ',
            'title_en': 'Unnamed'
        })
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_delete_event_series(self):
        ''' Test delete event series '''
        response = self.client.delete('/api/category/event-series/{}/'.format(self.to_be_it.id))
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
