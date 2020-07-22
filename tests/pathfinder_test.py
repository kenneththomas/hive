import unittest
import sys
import collections
sys.path.insert(0, '../pyengine')
sys.path.insert(1, 'pyengine')
import dfix as dfix
import pathfinder as pf


class pathfindertest(unittest.TestCase):
    def setUp(self):
        pass

    def test_single_destination(self):
        test_file = open('tests/resources/single_destination.json','r')
        destination = pf.pathfinder(test_file.read())
        test_file.close()
        self.assertEqual(destination,'maspeth:exch1')

    def test_single_destination_unavailable(self):
        test_file = open('tests/resources/single_destination_unavailable.json','r')
        destination = pf.pathfinder(test_file.read())
        test_file.close()
        self.assertFalse(destination)

    def test_bad_routetype(self):
        test_file = open('tests/resources/bad_routetype.json','r')
        destination = pf.pathfinder(test_file.read())
        test_file.close()
        self.assertFalse(destination)

if __name__ == '__main__':
    unittest.main()