import sys
sys.path.insert(0, '../pyengine')
sys.path.insert(1, 'pyengine')
import baripool
import random as r
import uuid
import time
from collections import OrderedDict
import unittest

class TestOrderMatchingSimulator(unittest.TestCase):

    def test_add_order(self):
        order_fix = "11=1001;54=1;55=AAPL;38=100;44=150"
        baripool.on_new_order(order_fix)
        self.assertEqual(len(baripool.bookshelf['AAPL']), 1)

    def test_match_full_quantity(self):
        # Add a buy order
        buy_order_fix = "11=1001;54=1;55=ZVZZT;38=100;44=150"
        baripool.on_new_order(buy_order_fix)

        # Add a sell order with matching price
        sell_order_fix = "11=1002;54=2;55=ZVZZT;38=100;44=150"
        baripool.on_new_order(sell_order_fix)

        self.assertEqual(len(baripool.bookshelf['ZVZZT']), 0)

    def test_no_match_different_prices(self):
        # Add a buy order
        buy_order_fix = "11=1001;54=1;55=MSFT;38=100;44=150"
        baripool.on_new_order(buy_order_fix)

        # Add a sell order with a higher price
        sell_order_fix = "11=1002;54=2;55=MSFT;38=100;44=155"
        baripool.on_new_order(sell_order_fix)

        self.assertEqual(len(baripool.bookshelf['MSFT']), 2)

    def test_match_partial_quantity(self):
        # Add a buy order
        buy_order_fix = "11=1001;54=1;55=BAC;38=100;44=150"
        baripool.on_new_order(buy_order_fix)

        # Add a sell order with a matching price but lower quantity
        sell_order_fix = "11=1002;54=2;55=BAC;38=80;44=150"
        baripool.on_new_order(sell_order_fix)

        self.assertEqual(len(baripool.bookshelf['BAC']), 1)
        self.assertEqual(baripool.bookshelf['BAC'][0].qty, 20)

class TestOrderCancellation(unittest.TestCase):
    def setUp(self):
        baripool.bookshelf.clear()

    def test_cancel_order_in_book(self):
        new_order = "8=FIX.4.2;11=1234;54=1;55=AAPL;38=100;44=150.00"
        baripool.on_new_order(new_order)
        baripool.on_cancel_order("1234")
        self.assertTrue(baripool.bookshelf['AAPL'][0].is_canceled)

    #TBD
    def test_cancel_order_not_in_book(self):
        baripool.on_cancel_order("5678")
        # Test if the appropriate message is printed when the order is not found in the order book

    #TBD
    def test_cancel_order_already_canceled(self):
        new_order = "8=FIX.4.2;11=2345;54=1;55=AAPL;38=100;44=150.00"
        baripool.on_new_order(new_order)
        baripool.on_cancel_order("2345")
        baripool.on_cancel_order("2345")
        # Test if the appropriate message is printed when the order is already canceled

if __name__ == '__main__':
    unittest.main()