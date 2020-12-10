'''
    Generator Application Tests
    generator/tests.py
    @author Teerapat Kraisrisirikul (810Teams)
'''

from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from community.models import Event, Club
from generator.models import QRCode, JoinKey, GeneratedDocx
from membership.models import Membership

import datetime


class QRCodeAPITest(APITestCase):
    ''' QR code API test '''
    def setUp(self):
        ''' Set up '''
        self.user_01 = get_user_model().objects.create_user(username='user_01', password='12345678', name='User One')
        self.user_02 = get_user_model().objects.create_user(username='user_02', password='12345678', name='User Two')
        self.user_03 = get_user_model().objects.create_user(username='user_03', password='12345678', name='User Three')
        self.user_04 = get_user_model().objects.create_user(username='user_04', password='12345678', name='User Four')
        self.user_05 = get_user_model().objects.create_user(username='user_05', password='12345678', name='User Five')
        self.event = Event.objects.create(
            name_th='กิจกรรมทดสอบรหัสคิวอาร์',
            name_en='QR Code API Test Event',
            is_approved=True,
            location='L203 IT KMITL',
            start_date=datetime.date(2020, 12, 1),
            end_date=datetime.date(2020, 12, 2),
            start_time=datetime.time(9, 0, 0),
            end_time=datetime.time(17, 0, 0)
        )

        Membership.objects.create(community_id=self.event.id, user_id=self.user_01.id, position=3)
        Membership.objects.create(community_id=self.event.id, user_id=self.user_02.id, position=2)
        Membership.objects.create(community_id=self.event.id, user_id=self.user_03.id, position=1)
        Membership.objects.create(community_id=self.event.id, user_id=self.user_04.id, position=0)

    def test_qr_code_leader(self):
        ''' Test QR code as leader '''
        self._test_crud(
            'user_01',
            create_code=status.HTTP_201_CREATED,
            retrieve_code=status.HTTP_200_OK,
            delete_code=status.HTTP_204_NO_CONTENT
        )

    def test_qr_code_deputy_leader(self):
        ''' Test QR code as deputy leader '''
        self._test_crud(
            'user_02',
            create_code=status.HTTP_201_CREATED,
            retrieve_code=status.HTTP_200_OK,
            delete_code=status.HTTP_204_NO_CONTENT
        )

    def test_qr_code_staff(self):
        ''' Test QR code as staff '''
        self._test_crud(
            'user_03',
            create_code=status.HTTP_400_BAD_REQUEST,
            retrieve_code=status.HTTP_200_OK,
            delete_code=status.HTTP_403_FORBIDDEN
        )

    def test_qr_code_member(self):
        ''' Test QR code as member '''
        self._test_crud(
            'user_04',
            create_code=status.HTTP_400_BAD_REQUEST,
            retrieve_code=status.HTTP_200_OK,
            delete_code=status.HTTP_403_FORBIDDEN
        )

    def test_qr_code_non_member(self):
        ''' Test QR code as non-member '''
        self._test_crud(
            'user_05',
            create_code=status.HTTP_400_BAD_REQUEST,
            retrieve_code=status.HTTP_403_FORBIDDEN,
            delete_code=status.HTTP_403_FORBIDDEN
        )

    def test_create_qr_code_duplicate(self):
        ''' Test create QR code duplicate '''
        self.client.login(username='user_01', password='12345678')

        QRCode.objects.create(url='https://www.google.com/', event_id=self.event.id)
        response = self.client.post('/api/generator/qr-code/', {
            'url': 'https://www.google.com/',
            'event': self.event.id
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.client.logout()

    def test_create_qr_code_url(self):
        ''' Test create QR code with valid and invalid URLs '''
        self.client.login(username='user_01', password='12345678')

        valid_urls = (
            'https://genshin.gg/',
            'https://www.google.com/',
            'https://www.reg.kmitl.ac.th/index/',
            'https://www.youtube.com/watch?v=yUjlBfmkO6g&t=287s&ab_channel=TheSoulofWind',
            'https://myanimelist.net/animelist/810Teams?order=4&order2=1&status=7&tag=anime'
        )
        invalid_urls = ('Google', 'Hello world', 'genshin.gg', 'yt98xasi12-sda', 'I love KMITL!')

        for url in valid_urls:
            response = self.client.post('/api/generator/qr-code/', {
                'url': url,
                'event': self.event.id
            })
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)

            try:
                QRCode.objects.get(id=response.data['id']).delete()
            except KeyError:
                pass

        for url in invalid_urls:
            response = self.client.post('/api/generator/qr-code/', {
                'url': url,
                'event': self.event.id
            })
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

            try:
                QRCode.objects.get(id=response.data['id']).delete()
            except KeyError:
                pass

        self.client.logout()

    def _test_crud(self, user_id, create_code=201, retrieve_code=200, update_code=405, delete_code=204):
        ''' Testing CRUD function '''
        self.client.login(username=user_id, password='12345678')

        # Create
        response = self._create()
        self.assertEqual(response.status_code, create_code)

        # Retrieve
        response = self._retrieve()
        self.assertEqual(response.status_code, retrieve_code)

        # Update
        response = self._update()
        self.assertEqual(response.status_code, update_code)

        # Delete
        response = self._delete()
        self.assertEqual(response.status_code, delete_code)

        self.client.logout()

    def _create(self):
        ''' Create QR code function '''
        response = self.client.post('/api/generator/qr-code/', {
            'url': 'https://www.google.com/',
            'event': self.event.id
        })

        try:
            QRCode.objects.get(id=response.data['id']).delete()
        except KeyError:
            pass

        return response

    def _retrieve(self):
        ''' Retrieve QR code function '''
        qr_code = QRCode.objects.create(url='https://www.google.com/', event_id=self.event.id)
        response = self.client.get('/api/generator/qr-code/{}/'.format(qr_code.id))
        qr_code.delete()

        return response

    def _update(self):
        ''' Update QR code function '''
        qr_code = QRCode.objects.create(url='https://www.google.com/', event_id=self.event.id)
        response = self.client.patch('/api/generator/qr-code/{}/'.format(qr_code.id), {
            'url': 'https://www.youtube.com/'
        })
        qr_code.delete()

        return response

    def _delete(self):
        ''' Delete QR code function '''
        qr_code = QRCode.objects.create(url='https://www.google.com/', event_id=self.event.id)
        return self.client.delete('/api/generator/qr-code/{}/'.format(qr_code.id))


class JoinKeyAPITest(APITestCase):
    ''' Join key API test '''
    def setUp(self):
        ''' Set up '''
        self.user_01 = get_user_model().objects.create_user(username='user_01', password='12345678', name='User One')
        self.user_02 = get_user_model().objects.create_user(username='user_02', password='12345678', name='User Two')
        self.user_03 = get_user_model().objects.create_user(username='user_03', password='12345678', name='User Three')
        self.user_04 = get_user_model().objects.create_user(username='user_04', password='12345678', name='User Four')
        self.user_05 = get_user_model().objects.create_user(username='user_05', password='12345678', name='User Five')
        self.event = Event.objects.create(
            name_th='กิจกรรมทดสอบรหัสเข้าร่วม',
            name_en='Join Key Test Event',
            is_approved=True,
            location='L205 IT KMITL',
            start_date=datetime.date(2020, 12, 1),
            end_date=datetime.date(2020, 12, 2),
            start_time=datetime.time(9, 0, 0),
            end_time=datetime.time(17, 0, 0)
        )

        Membership.objects.create(community_id=self.event.id, user_id=self.user_01.id, position=3)
        Membership.objects.create(community_id=self.event.id, user_id=self.user_02.id, position=2)
        Membership.objects.create(community_id=self.event.id, user_id=self.user_03.id, position=1)
        Membership.objects.create(community_id=self.event.id, user_id=self.user_04.id, position=0)

    def test_join_key_leader(self):
        ''' Test join key as leader '''
        self._test_crud(
            'user_01',
            create_code=status.HTTP_201_CREATED,
            retrieve_code=status.HTTP_200_OK,
            delete_code=status.HTTP_204_NO_CONTENT
        )

    def test_join_key_deputy_leader(self):
        ''' Test join key as deputy leader '''
        self._test_crud(
            'user_02',
            create_code=status.HTTP_201_CREATED,
            retrieve_code=status.HTTP_200_OK,
            delete_code=status.HTTP_204_NO_CONTENT
        )

    def test_join_key_staff(self):
        ''' Test join key as staff '''
        self._test_crud(
            'user_03',
            create_code=status.HTTP_400_BAD_REQUEST,
            retrieve_code=status.HTTP_200_OK,
            delete_code=status.HTTP_403_FORBIDDEN
        )

    def test_join_key_member(self):
        ''' Test join key as member '''
        self._test_crud(
            'user_04',
            create_code=status.HTTP_400_BAD_REQUEST,
            retrieve_code=status.HTTP_200_OK,
            delete_code=status.HTTP_403_FORBIDDEN
        )

    def test_join_key_non_member(self):
        ''' Test join key as non-member '''
        self._test_crud(
            'user_05',
            create_code=status.HTTP_400_BAD_REQUEST,
            retrieve_code=status.HTTP_403_FORBIDDEN,
            delete_code=status.HTTP_403_FORBIDDEN
        )

    def test_create_join_key_duplicate(self):
        ''' Test create join key duplicate '''
        self.client.login(username='user_01', password='12345678')

        JoinKey.objects.create(key='abcdefgh0134567', event_id=self.event.id)
        response = self.client.post('/api/generator/join-key/', {
            'key': 'abcdefgh0134567x',
            'event': self.event.id
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.client.logout()

    def _test_crud(self, user_id, create_code=201, retrieve_code=200, update_code=405, delete_code=204):
        ''' Testing CRUD function '''
        self.client.login(username=user_id, password='12345678')

        # Create
        response = self._create()
        self.assertEqual(response.status_code, create_code)

        # Retrieve
        response = self._retrieve()
        self.assertEqual(response.status_code, retrieve_code)

        # Update
        response = self._update()
        self.assertEqual(response.status_code, update_code)

        # Delete
        response = self._delete()
        self.assertEqual(response.status_code, delete_code)

        self.client.logout()

    def _create(self):
        ''' Create join key function '''
        response = self.client.post('/api/generator/join-key/', {
            'key': 'abcdefgh01234567',
            'event': self.event.id
        })

        try:
            JoinKey.objects.get(id=response.data['id']).delete()
        except KeyError:
            pass

        return response

    def _retrieve(self):
        ''' Retrieve join key function '''
        join_key = JoinKey.objects.create(key='abcdefgh01234567', event_id=self.event.id)
        response = self.client.get('/api/generator/join-key/{}/'.format(join_key.id))
        join_key.delete()

        return response

    def _update(self):
        ''' Update join key function '''
        join_key = JoinKey.objects.create(key='abcdefgh01234567', event_id=self.event.id)
        response = self.client.patch('/api/generator/join-key/{}/'.format(join_key.id), {
            'key': 'abcdefgh01234567x',
        })
        join_key.delete()

        return response

    def _delete(self):
        ''' Delete join key function '''
        join_key = JoinKey.objects.create(key='abcdefgh01234567', event_id=self.event.id)
        return self.client.delete('/api/generator/join-key/{}/'.format(join_key.id))


class GenerateJoinKeyAPITest(APITestCase):
    ''' Generate join key API test '''
    def test_generate_join_key_length_matching(self):
        ''' Test generate join key length matching '''
        for i in (8, 16, 32, 48, 64):
            response = self.client.get('/api/generator/join-key/generate/?length={}'.format(i))
            self.assertEqual(len(response.data['key']), i)

    def test_generate_join_key_length_validity(self):
        ''' Test generate join key length validity '''
        response = self.client.get('/api/generator/join-key/generate/?length=7')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.client.get('/api/generator/join-key/generate/?length=8')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.get('/api/generator/join-key/generate/?length=64')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.get('/api/generator/join-key/generate/?length=65')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class UseJoinKey(APITestCase):
    ''' Use join key API test '''
    def setUp(self):
        ''' Set up '''
        self.user_01 = get_user_model().objects.create_user(username='user_01', password='12345678')
        self.user_02 = get_user_model().objects.create_user(username='user_02', password='12345678')
        self.event = Event.objects.create(
            name_th='กิจกรรมทดสอบเข้าร่วมด้วยรหัสเข้าร่วม',
            name_en='Joining by Join Key Test Event',
            is_approved=True,
            location='L207 IT KMITL',
            start_date=datetime.date(2020, 12, 1),
            end_date=datetime.date(2020, 12, 2),
            start_time=datetime.time(9, 0, 0),
            end_time=datetime.time(17, 0, 0)
        )
        self.join_key = JoinKey.objects.create(event_id=self.event.id, key='abcdefgh01234567')

        Membership.objects.create(community_id=self.event.id, user_id=self.user_01.id, position=3)

    def test_use_join_key_non_member(self):
        ''' Test use join key '''
        self.client.login(username='user_02', password='12345678')

        self.assertEqual(len(Membership.objects.all()), 1)
        self.client.post('/api/generator/join-key/use/', {
            'key': 'abcdefgh01234567'
        })
        self.assertEqual(len(Membership.objects.all()), 2)

    def test_use_join_key_member(self):
        ''' Test use join key '''
        self.client.login(username='user_01', password='12345678')

        response = self.client.post('/api/generator/join-key/use/', {
            'key': 'abcdefgh01234567'
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_use_join_key_invalid_join_key(self):
        ''' Test use join key '''
        self.client.login(username='user_02', password='12345678')

        response = self.client.post('/api/generator/join-key/use/', {
            'key': '00000000'
        })
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class GeneratedDocxAPITest(APITestCase):
    ''' Generated Microsoft Word document API test '''
    def setUp(self):
        ''' Set up '''
        self.user_01 = get_user_model().objects.create_user(username='user_01', password='12345678', name='User One')
        self.user_02 = get_user_model().objects.create_user(username='user_02', password='12345678', name='User Two')
        self.user_03 = get_user_model().objects.create_user(username='user_03', password='12345678', name='User Three')
        self.user_04 = get_user_model().objects.create_user(username='user_04', password='12345678', name='User Four')
        self.user_05 = get_user_model().objects.create_user(username='user_05', password='12345678', name='User Five')
        self.lecturer = get_user_model().objects.create_user(
            username='lecturer', password='12345678', name='Prof.Lazy Bones', user_group='lecturer'
        )
        self.club = Club.objects.create(name_th='ชุมนุมทดสอบสร้างเอกสาร', name_en='Document Generating Club')

        Membership.objects.create(community_id=self.club.id, user_id=self.user_01.id, position=3)
        Membership.objects.create(community_id=self.club.id, user_id=self.user_02.id, position=2)
        Membership.objects.create(community_id=self.club.id, user_id=self.user_03.id, position=1)
        Membership.objects.create(community_id=self.club.id, user_id=self.user_04.id, position=0)

    def test_generated_docx_leader(self):
        ''' Test generated Microsoft Word document as leader '''
        self._test_crud(
            'user_01',
            create_code=status.HTTP_201_CREATED,
            retrieve_code=status.HTTP_200_OK,
            update_code=status.HTTP_200_OK,
            delete_code=status.HTTP_204_NO_CONTENT
        )

    def test_generated_docx_deputy_leader(self):
        ''' Test generated Microsoft Word document as deputy leader '''
        self._test_crud(
            'user_02',
            create_code=status.HTTP_201_CREATED,
            retrieve_code=status.HTTP_200_OK,
            update_code=status.HTTP_200_OK,
            delete_code=status.HTTP_204_NO_CONTENT
        )

    def test_generated_docx_staff(self):
        ''' Test generated Microsoft Word document as staff '''
        self._test_crud(
            'user_03',
            create_code=status.HTTP_400_BAD_REQUEST,
            retrieve_code=status.HTTP_403_FORBIDDEN,
            update_code=status.HTTP_403_FORBIDDEN,
            delete_code=status.HTTP_403_FORBIDDEN
        )

    def test_generated_docx_member(self):
        ''' Test generated Microsoft Word document as member '''
        self._test_crud(
            'user_04',
            create_code=status.HTTP_400_BAD_REQUEST,
            retrieve_code=status.HTTP_403_FORBIDDEN,
            update_code=status.HTTP_403_FORBIDDEN,
            delete_code=status.HTTP_403_FORBIDDEN
        )

    def test_generated_docx_non_member(self):
        ''' Test generated Microsoft Word document as non-member '''
        self._test_crud(
            'user_05',
            create_code=status.HTTP_400_BAD_REQUEST,
            retrieve_code=status.HTTP_403_FORBIDDEN,
            update_code=status.HTTP_403_FORBIDDEN,
            delete_code=status.HTTP_403_FORBIDDEN
        )

    def test_create_generated_docx_duplicate(self):
        ''' Test create generated Microsoft Word document duplicate '''
        self.client.login(username='user_01', password='12345678')

        GeneratedDocx.objects.create(
            club_id=self.club.id,
            advisor_id=self.lecturer.id,
            objective='objective',
            objective_list='objective_list',
            room='room',
            schedule='schedule',
            plan_list='plan_list',
            merit='merit'
        )
        response = self.client.post('/api/generator/docx/', {
            'club': self.club.id,
            'advisor': self.lecturer.id,
            'objective': 'objective',
            'objective_list': 'objective_list',
            'room': 'room',
            'schedule': 'schedule',
            'plan_list': 'plan_list',
            'merit': 'merit'
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.client.logout()

    def _test_crud(self, user_id, create_code=201, retrieve_code=200, update_code=405, delete_code=204):
        ''' Testing CRUD function '''
        self.client.login(username=user_id, password='12345678')

        # Create
        response = self._create()
        self.assertEqual(response.status_code, create_code)

        # Retrieve
        response = self._retrieve()
        self.assertEqual(response.status_code, retrieve_code)

        # Update
        response = self._update()
        self.assertEqual(response.status_code, update_code)

        # Delete
        response = self._delete()
        self.assertEqual(response.status_code, delete_code)

        self.client.logout()

    def _create(self):
        ''' Create generated Microsoft Word document function '''
        response = self.client.post('/api/generator/docx/', {
            'club': self.club.id,
            'advisor': self.lecturer.id,
            'objective': 'objective',
            'objective_list': 'objective_list',
            'room': 'room',
            'schedule': 'schedule',
            'plan_list': 'plan_list',
            'merit': 'merit'
        })

        try:
            GeneratedDocx.objects.get(id=response.data['id']).delete()
        except KeyError:
            pass

        return response

    def _retrieve(self):
        ''' Retrieve generated Microsoft Word document function '''
        generated_docx = GeneratedDocx.objects.create(
            club_id=self.club.id,
            advisor_id=self.lecturer.id,
            objective='objective',
            objective_list='objective_list',
            room='room',
            schedule='schedule',
            plan_list='plan_list',
            merit='merit'
        )
        response = self.client.get('/api/generator/docx/{}/'.format(generated_docx.id))
        generated_docx.delete()

        return response

    def _update(self):
        ''' Update generated Microsoft Word document function '''
        generated_docx = GeneratedDocx.objects.create(
            club_id=self.club.id,
            advisor_id=self.lecturer.id,
            objective='objective',
            objective_list='objective_list',
            room='room',
            schedule='schedule',
            plan_list='plan_list',
            merit='merit'
        )
        response = self.client.patch('/api/generator/docx/{}/'.format(generated_docx.id), {
            'room': '509'
        })
        generated_docx.delete()

        return response

    def _delete(self):
        ''' Delete generated Microsoft Word document function '''
        generated_docx = GeneratedDocx.objects.create(
            club_id=self.club.id,
            advisor_id=self.lecturer.id,
            objective='objective',
            objective_list='objective_list',
            room='room',
            schedule='schedule',
            plan_list='plan_list',
            merit='merit'
        )
        return self.client.delete('/api/generator/docx/{}/'.format(generated_docx.id))
