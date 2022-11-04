from cgi import test
from re import T
import unittest
import sys
import collections
sys.path.insert(0, '../pyengine')
sys.path.insert(1, 'pyengine')
import dfix
import yeet
import uuid
import datetime
from yeet_test import testutils

class perftest(unittest.TestCase):

    #send 1000 orders and check time to process
    def test_1000_orders(self):
        import time
        start_time = time.time()
        for i in range(1000):
            yeet.parse_new_msg(testutils.generic_order())
        print("--- %s seconds ---" % (time.time() - start_time))
        #if less than 1 second, pass
        self.assertTrue((time.time() - start_time) < 1)

if __name__ == '__main__':
    unittest.main()