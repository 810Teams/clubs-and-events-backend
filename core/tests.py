'''
    Core Application Tests
    core/tests.py
    @author Teerapat Kraisrisirikul (810Teams)
'''

from django.test import TestCase

from core.utils.files import simplify_file_size


class FilesUtilityTest(TestCase):
    ''' Utility test '''
    def test_simplify_file_size(self):
        ''' Test simplify file size function '''
        self.assertEqual(simplify_file_size(7, unit='b'), '7 bits')
        self.assertEqual(simplify_file_size(8, unit='b'), '1 bytes')
        self.assertEqual(simplify_file_size(9, unit='b'), '1 bytes')
        self.assertEqual(simplify_file_size(8191, unit='b'), '1023 bytes')
        self.assertEqual(simplify_file_size(8192, unit='b'), '1.00 kB')
        self.assertEqual(simplify_file_size(8193, unit='b'), '1.00 kB')
        self.assertEqual(simplify_file_size(8388607, unit='b'), '1023.99 kB')
        self.assertEqual(simplify_file_size(8388608, unit='b'), '1.00 MB')
        self.assertEqual(simplify_file_size(8388609, unit='b'), '1.00 MB')

        self.assertEqual(simplify_file_size(1023, unit='B'), '1023 bytes')
        self.assertEqual(simplify_file_size(1024, unit='B'), '1.00 kB')
        self.assertEqual(simplify_file_size(1025, unit='B'), '1.00 kB')
        self.assertEqual(simplify_file_size(1048575, unit='B'), '1023.99 kB')
        self.assertEqual(simplify_file_size(1048576, unit='B'), '1.00 MB')
        self.assertEqual(simplify_file_size(1048577, unit='B'), '1.00 MB')
        self.assertEqual(simplify_file_size(1073741823, unit='B'), '1023.99 MB')
        self.assertEqual(simplify_file_size(1073741824, unit='B'), '1.00 GB')
        self.assertEqual(simplify_file_size(1073741825, unit='B'), '1.00 GB')

        self.assertEqual(simplify_file_size(1023, unit='kB'), '1023.00 kB')
        self.assertEqual(simplify_file_size(1024, unit='kB'), '1.00 MB')
        self.assertEqual(simplify_file_size(1025, unit='kB'), '1.00 MB')
        self.assertEqual(simplify_file_size(1048575, unit='kB'), '1023.99 MB')
        self.assertEqual(simplify_file_size(1048576, unit='kB'), '1.00 GB')
        self.assertEqual(simplify_file_size(1048577, unit='kB'), '1.00 GB')
        self.assertEqual(simplify_file_size(1073741823, unit='kB'), '1023.99 GB')
        self.assertEqual(simplify_file_size(1073741824, unit='kB'), '1.00 TB')
        self.assertEqual(simplify_file_size(1073741825, unit='kB'), '1.00 TB')
