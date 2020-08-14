import unittest
import sys
import collections
sys.path.insert(0, '../pyengine')
sys.path.insert(1, 'pyengine')
import dfix as dfix
import pathfinder as pf
import json

testroutes_map = {}

def test_parse_routes():
    # we will have one json file which will contain all routes for these tests.
    # this function is required to split them into individual jsons which we will store in a python dict
    test_file = open('tests/resources/routing_tests.json')
    routes = test_file.read()
    routesparse = json.loads(routes)

    for route in routesparse['testroutes']:
        testroutes_map[route['routeid']] = json.dumps(route,indent=2)

    print(testroutes_map)

    test_file.close()

class pathfindertest(unittest.TestCase):
    def setUp(self):
        test_parse_routes()
        pass

    def test_single_destination(self):
        test_route = testroutes_map['single_destination_test']
        destination = pf.pathfinder(test_route)
        self.assertEqual(destination,'maspeth:exch1')

    def test_single_destination_unavailable(self):
        test_route = testroutes_map['single_destination_test_unavailable']
        destination = pf.pathfinder(test_route)
        self.assertFalse(destination)

    def test_bad_routetype(self):
        test_route = testroutes_map['bad_routetype_test']
        destination = pf.pathfinder(test_route)
        self.assertFalse(destination)

    def test_priority_dest1(self):
        test_route = testroutes_map['priority_test_dest1']
        destination = pf.pathfinder(test_route)
        self.assertEqual(destination,'maspeth:exch1')

    def test_priority_dest3(self):
        test_route = testroutes_map['priority_test_dest3']
        destination = pf.pathfinder(test_route)
        self.assertEqual(destination,'bushwick:exch1')

if __name__ == '__main__':
    unittest.main()