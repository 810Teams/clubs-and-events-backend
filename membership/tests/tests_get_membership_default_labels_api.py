'''
    Membership Application's Get Membership Default Labels API Test
    membership/tests/tests_get_membership_default_labels_api.py
    @author Teerapat Kraisrisirikul (810Teams)
'''

from rest_framework import status
from rest_framework.test import APITestCase


class GetMembershipDefaultLabelsAPITest(APITestCase):
    ''' Get membership default labels API test '''
    def test_retrieve_default_membership_labels(self):
        ''' Test retrieve default membership labels '''
        response = self.client.get('/api/membership/membership/label/default/')

        # Response status assertion
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Length assertion
        self.assertEqual(len(response.data), 4)

        # Keys assertion
        for i in range(4):
            self.assertIn('position', response.data[i].keys())
            self.assertIn('labels', response.data[i].keys())
            self.assertIn('labels_th', response.data[i].keys())

            self.assertIsInstance(response.data[i]['position'], int)
            self.assertIsInstance(response.data[i]['labels'], dict)
            self.assertIsInstance(response.data[i]['labels_th'], dict)

        # Community types assertion
        for i in range(4):
            self.assertIn('club', response.data[i]['labels'].keys())
            self.assertIn('event', response.data[i]['labels'].keys())
            self.assertIn('community_event', response.data[i]['labels'].keys())
            self.assertIn('lab', response.data[i]['labels'].keys())

            self.assertIsInstance(response.data[i]['labels']['club'], str)
            self.assertIsInstance(response.data[i]['labels']['event'], str)
            self.assertIsInstance(response.data[i]['labels']['community_event'], str)
            self.assertIsInstance(response.data[i]['labels']['lab'], str)

            self.assertIn('club', response.data[i]['labels_th'].keys())
            self.assertIn('event', response.data[i]['labels_th'].keys())
            self.assertIn('community_event', response.data[i]['labels_th'].keys())
            self.assertIn('lab', response.data[i]['labels_th'].keys())

            self.assertIsInstance(response.data[i]['labels_th']['club'], str)
            self.assertIsInstance(response.data[i]['labels_th']['event'], str)
            self.assertIsInstance(response.data[i]['labels_th']['community_event'], str)
            self.assertIsInstance(response.data[i]['labels_th']['lab'], str)


    def test_create_default_membership_labels(self):
        ''' Test create default membership labels '''
        response = self.client.post('/api/membership/membership/label/default/', {})
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_default_membership_labels(self):
        ''' Test update default membership labels '''
        response = self.client.put('/api/membership/membership/label/default/', {})
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.patch('/api/membership/membership/label/default/', {})
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_delete_default_membership_labels(self):
        ''' Test delete default membership labels '''
        response = self.client.delete('/api/membership/membership/label/default/')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
