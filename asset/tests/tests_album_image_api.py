'''
    Asset Application's Album Image API Test
    asset/tests/tests_album_image_api.py
    @author Teerapat Kraisrisirikul (810Teams)
'''

from django.contrib.auth import get_user_model
from django.core.files.images import ImageFile
from rest_framework import status
from rest_framework.test import APITestCase

from asset.models import Album, AlbumImage
from community.models import Club
from membership.models import Membership


class AlbumImageAPITest(APITestCase):
    ''' Album image API test '''
    def setUp(self):
        ''' Set up '''
        self.user_01 = get_user_model().objects.create_user(username='user_01', password='12345678', name='User One')
        self.user_02 = get_user_model().objects.create_user(username='user_02', password='12345678', name='User Two')
        self.user_03 = get_user_model().objects.create_user(username='user_03', password='12345678', name='User Three')
        self.user_04 = get_user_model().objects.create_user(username='user_04', password='12345678', name='User Four')
        self.user_05 = get_user_model().objects.create_user(username='user_05', password='12345678', name='User Five')
        self.club_public = Club.objects.create(
            name_th='ชุมนุมทดสอบภาพอัลบั้ม สาธารณะ', name_en='Album Image Testing Club (Public)',
            is_publicly_visible=True, is_official=True
        )
        self.club_private = Club.objects.create(
            name_th='ชุมนุมทดสอบภาพอัลบั้ม ส่วนตัว', name_en='Album Image Testing Club (Private)',
            is_publicly_visible=False, is_official=False
        )

        Membership.objects.create(community_id=self.club_public.id, user_id=self.user_01.id, position=3)
        Membership.objects.create(community_id=self.club_public.id, user_id=self.user_02.id, position=2)
        Membership.objects.create(community_id=self.club_public.id, user_id=self.user_03.id, position=1)
        Membership.objects.create(community_id=self.club_public.id, user_id=self.user_04.id, position=0)

        Membership.objects.create(community_id=self.club_private.id, user_id=self.user_01.id, position=3)
        Membership.objects.create(community_id=self.club_private.id, user_id=self.user_02.id, position=2)
        Membership.objects.create(community_id=self.club_private.id, user_id=self.user_03.id, position=1)
        Membership.objects.create(community_id=self.club_private.id, user_id=self.user_04.id, position=0)

        self.album_public = Album.objects.create(community_id=self.club_public.id, name='Public Club Album')
        self.album_private = Album.objects.create(community_id=self.club_private.id, name='Private Club Album')

    def test_list_album_image_authenticated(self):
        ''' Test list album image while authenticated '''
        self.client.login(username='user_05', password='12345678')

        AlbumImage.objects.create(album_id=self.album_public.id, image=ImageFile(open_image('01')))
        AlbumImage.objects.create(album_id=self.album_public.id, image=ImageFile(open_image('02')))
        AlbumImage.objects.create(album_id=self.album_private.id, image=ImageFile(open_image('03')))
        response = self.client.get('/api/asset/album/image/')
        self.assertEqual(len(response.data), 3)

        self.client.logout()

    def test_list_album_image_unauthenticated(self):
        ''' Test list album image while unauthenticated '''
        AlbumImage.objects.create(album_id=self.album_public.id, image=ImageFile(open_image('01')))
        AlbumImage.objects.create(album_id=self.album_public.id, image=ImageFile(open_image('02')))
        AlbumImage.objects.create(album_id=self.album_private.id, image=ImageFile(open_image('03')))
        response = self.client.get('/api/asset/album/image/')
        self.assertEqual(len(response.data), 2)

    def test_retrieve_album_image_authenticated(self):
        ''' Test retrieve album image while authenticated '''
        self.client.login(username='user_05', password='12345678')

        image = AlbumImage.objects.create(album_id=self.album_public.id, image=ImageFile(open_image('01')))
        response = self.client.get('/api/asset/album/image/{}/'.format(image.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        image = AlbumImage.objects.create(album_id=self.album_private.id, image=ImageFile(open_image('02')))
        response = self.client.get('/api/asset/album/image/{}/'.format(image.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.client.logout()

    def test_retrieve_album_image_unauthenticated(self):
        ''' Test retrieve album image while unauthenticated '''
        image = AlbumImage.objects.create(album_id=self.album_public.id, image=ImageFile(open_image('01')))
        response = self.client.get('/api/asset/album/image/{}/'.format(image.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        image = AlbumImage.objects.create(album_id=self.album_private.id, image=ImageFile(open_image('02')))
        response = self.client.get('/api/asset/album/image/{}/'.format(image.id))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_album_image_as_leader(self):
        ''' Test create album image as leader '''
        self._test_create_album_image_as(username='user_01', album_id=self.album_public.id, allows_create=True)

    def test_create_album_image_as_deputy_leader(self):
        ''' Test create album image as deputy leader '''
        self._test_create_album_image_as(username='user_02', album_id=self.album_public.id, allows_create=True)

    def test_create_album_image_as_staff(self):
        ''' Test create album image as staff '''
        self._test_create_album_image_as(username='user_03', album_id=self.album_public.id, allows_create=True)

    def test_create_album_image_as_member(self):
        ''' Test create album image as member '''
        self._test_create_album_image_as(username='user_04', album_id=self.album_public.id, allows_create=False)

    def test_create_album_image_as_non_member(self):
        ''' Test create album image as non-member '''
        self._test_create_album_image_as(username='user_05', album_id=self.album_public.id, allows_create=False)

    def test_create_album_image_as_guest(self):
        ''' Test create album image as guest '''
        self._test_create_album_image_as(username=str(), album_id=self.album_public.id, allows_create=False)

    def _test_create_album_image_as(self, username=str(), album_id=int(), allows_create=True):
        ''' Test create album image as different membership positions '''
        if username.strip() != str():
            self.client.login(username=username, password='12345678')

        with open_image('01') as data:
            response = self.client.post('/api/asset/album/image/', {
                'album': album_id,
                'image': data
            }, format='multipart')

        if allows_create:
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        elif username.strip() == str():
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        else:
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        if username.strip() != str():
            self.client.logout()

    def test_update_album_image(self):
        ''' Test update album image '''
        self.client.login(username='user_01', password='12345678')

        image = AlbumImage.objects.create(album_id=self.album_public.id, image=ImageFile(open_image('01')))

        with open_image('02') as data:
            response = self.client.patch('/api/asset/album/image/{}/'.format(image.id), {
                'image': data
            }, format='multipart')

        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        self.client.logout()

    def test_delete_album_image_as_leader(self):
        ''' Test delete album image as leader '''
        self._test_delete_album_image_as(username='user_01', album_id=self.album_public.id, allows_delete=True)

    def test_delete_album_image_as_deputy_leader(self):
        ''' Test delete album image as deputy leader '''
        self._test_delete_album_image_as(username='user_02', album_id=self.album_public.id, allows_delete=True)

    def test_delete_album_image_as_staff(self):
        ''' Test delete album image as staff '''
        self._test_delete_album_image_as(username='user_03', album_id=self.album_public.id, allows_delete=True)

    def test_delete_album_image_as_member(self):
        ''' Test delete album image as member '''
        self._test_delete_album_image_as(username='user_04', album_id=self.album_public.id, allows_delete=False)

    def test_delete_album_image_as_non_member(self):
        ''' Test delete album image as non-member '''
        self._test_delete_album_image_as(username='user_05', album_id=self.album_public.id, allows_delete=False)

    def test_delete_album_image_as_guest(self):
        ''' Test delete album image as guest '''
        self._test_delete_album_image_as(username=str(), album_id=self.album_public.id, allows_delete=False)

    def _test_delete_album_image_as(self, username=str(), album_id=int(), allows_delete=True):
        ''' Test delete album image as different membership positions '''
        if username.strip() != str():
            self.client.login(username=username, password='12345678')

        image = AlbumImage.objects.create(album_id=album_id, image=ImageFile(open_image('03')))
        response = self.client.delete('/api/asset/album/image/{}/'.format(image.id))

        if allows_delete:
            self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        else:
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        if username.strip() != str():
            self.client.logout()


def open_image(name, extension='jpg'):
    ''' Open test image '''
    return open('asset/tests/img/{}.{}'.format(name, extension), 'rb')
