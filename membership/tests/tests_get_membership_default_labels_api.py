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

        # Community types assertion
        self.assertIn('club', response.data.keys())
        self.assertIn('event', response.data.keys())
        self.assertIn('community_event', response.data.keys())
        self.assertIn('lab', response.data.keys())

        # Membership positions assertion
        self.assertIn('3', response.data['club'])
        self.assertIn('2', response.data['club'])
        self.assertIn('1', response.data['club'])
        self.assertIn('0', response.data['club'])
        self.assertIn('3', response.data['event'])
        self.assertIn('2', response.data['event'])
        self.assertIn('1', response.data['event'])
        self.assertIn('0', response.data['event'])
        self.assertIn('3', response.data['community_event'])
        self.assertIn('2', response.data['community_event'])
        self.assertIn('1', response.data['community_event'])
        self.assertIn('0', response.data['community_event'])
        self.assertIn('3', response.data['lab'])
        self.assertIn('2', response.data['lab'])
        self.assertIn('1', response.data['lab'])
        self.assertIn('0', response.data['lab'])

        # Membership label type assertion
        self.assertIsInstance(response.data['club']['3'], str)
        self.assertIsInstance(response.data['club']['2'], str)
        self.assertIsInstance(response.data['club']['1'], str)
        self.assertIsInstance(response.data['club']['0'], str)
        self.assertIsInstance(response.data['event']['3'], str)
        self.assertIsInstance(response.data['event']['2'], str)
        self.assertIsInstance(response.data['event']['1'], str)
        self.assertIsInstance(response.data['event']['0'], str)
        self.assertIsInstance(response.data['community_event']['3'], str)
        self.assertIsInstance(response.data['community_event']['2'], str)
        self.assertIsInstance(response.data['community_event']['1'], str)
        self.assertIsInstance(response.data['community_event']['0'], str)
        self.assertIsInstance(response.data['lab']['3'], str)
        self.assertIsInstance(response.data['lab']['2'], str)
        self.assertIsInstance(response.data['lab']['1'], str)
        self.assertIsInstance(response.data['lab']['0'], str)

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
