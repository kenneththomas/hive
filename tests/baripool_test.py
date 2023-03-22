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


if __name__ == '__main__':
    unittest.main()