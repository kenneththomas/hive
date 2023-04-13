import sys
sys.path.insert(0, '../pyengine')
sys.path.insert(1, 'pyengine')
sys.path.insert(1, 'tests/resources')
import baripool
import random as r
import uuid
import time
from collections import OrderedDict
import unittest
import devresources as dr
import baripool_action as bpa

lastusedsendercomp = None

def random_sendercomp():
    # do not reuse lastusedsendercomp, if matched, try again
    global lastusedsendercomp
    while True:
        sendercomp = r.choice(list(dr.clients.keys()))
        if sendercomp != lastusedsendercomp:
            lastusedsendercomp = sendercomp
            return sendercomp

class TestOrderMatchingSimulator(unittest.TestCase):

    def test_add_order(self):
        order_fix = f"49={random_sendercomp()};11={bpa.neworderid()};54=1;55=AAPL;38=100;44=150"
        baripool.on_new_order(order_fix)
        self.assertEqual(len(baripool.bookshelf['AAPL']), 1)

    def test_match_full_quantity(self):
        # Add a buy order
        buy_order_fix = f"49={random_sendercomp()};11={bpa.neworderid()};54=1;55=ZVZZT;38=100;44=150"
        baripool.on_new_order(buy_order_fix)

        # Add a sell order with matching price
        sell_order_fix = f"49={random_sendercomp()};11={bpa.neworderid()};54=2;55=ZVZZT;38=100;44=150"
        baripool.on_new_order(sell_order_fix)

        self.assertEqual(len(baripool.bookshelf['ZVZZT']), 0)

    def test_no_match_different_prices(self):
        # Add a buy order
        buy_order_fix = f"49={random_sendercomp()};11={bpa.neworderid()};54=1;55=MSFT;38=100;44=150"
        baripool.on_new_order(buy_order_fix)

        # Add a sell order with a higher price
        sell_order_fix = f"49={random_sendercomp()};11={bpa.neworderid()};54=2;55=MSFT;38=100;44=155"
        baripool.on_new_order(sell_order_fix)

        self.assertEqual(len(baripool.bookshelf['MSFT']), 2)

    def test_match_partial_quantity(self):
        # Add a buy order
        buy_order_fix = f"49={random_sendercomp()};11={bpa.neworderid()};54=1;55=BAC;38=100;44=150"
        baripool.on_new_order(buy_order_fix)

        # Add a sell order with a matching price but lower quantity
        sell_order_fix = f"49={random_sendercomp()};11={bpa.neworderid()};54=2;55=BAC;38=80;44=150"
        baripool.on_new_order(sell_order_fix)

        self.assertEqual(len(baripool.bookshelf['BAC']), 1)
        self.assertEqual(baripool.bookshelf['BAC'][0].qty, 20)

    # test IOC order. add an IOC order and check that it is not in the bookshelf
    def test_ioc_order(self):
        # Add a buy order
        buy_order_fix = f"49={random_sendercomp()};11={bpa.neworderid()};54=1;55=TSLA;38=100;44=150;59=3"
        baripool.on_new_order(buy_order_fix)

        self.assertEqual(len(baripool.bookshelf['TSLA']), 0)


    # partial match IOC. add an IOC order that should fill partially and check that the remaining quantity is not in the bookshelf
    def test_partial_match_ioc_order(self):
        # Add a buy order
        buy_order_fix = f"49={random_sendercomp()};11={bpa.neworderid()};54=1;55=LULU;38=100;44=150;"
        baripool.on_new_order(buy_order_fix)

        # Add a sell order ioc order with matching price and higher quantity. The IOC order should fill partially and the remaining quantity should not be in the bookshelf
        sell_order_fix = f"49={random_sendercomp()};11={bpa.neworderid()};54=2;55=LULU;38=120;44=150;59=3"
        baripool.on_new_order(sell_order_fix)

        # add a buy order that would fill with the ioc. it should not fill because it was canceled
        buy_order_fix = f"49={random_sendercomp()};11={bpa.neworderid()};54=1;55=LULU;38=20;44=150;"
        baripool.on_new_order(buy_order_fix)

        #pass if open qty is 20
        baripool.display_book(baripool.bookshelf['LULU'])
        self.assertEqual(baripool.bookshelf['LULU'][0].qty, 20)

    # send market order + IOC, should not fill
    def test_market_order_ioc_nofill(self):
        # Add a buy order
        buy_order_fix = f"49={random_sendercomp()};11={bpa.neworderid()};54=1;55=TM;38=100;44=150;40=1;59=3;"
        result = baripool.on_new_order(buy_order_fix)
        # result should have 150=4
        self.assertTrue(result.find("150=4") > 0)

    def test_market_order_ioc_day_reject(self):
        # Add a buy order
        buy_order_fix = f"49={random_sendercomp()};11={bpa.neworderid()};54=1;55=FB;38=100;44=150;40=1;59=1;"
        result = baripool.on_new_order(buy_order_fix)
        # result should have 150=8
        self.assertTrue(result.find("150=8") > 0)

    def test_market_order_ioc_fill(self):
        # add a day limit order to match with
        buy_order_fix = f"49={random_sendercomp()};11={bpa.neworderid()};54=1;55=PINS;38=100;44=150;40=2;59=1;"
        baripool.on_new_order(buy_order_fix)
        # add a sell market order with IOC
        sell_order_fix = f"49={random_sendercomp()};11=iocmkt;54=2;55=PINS;38=100;44=150;40=1;59=3;"
        baripool.on_new_order(sell_order_fix)
        # check that the order is filled
        self.assertTrue(baripool.fillcontainer['iocmkt']['150'] == '2')

    # reject futures order
    def test_futures_order(self):
        # Add a buy order
        buy_order_fix = f"49={random_sendercomp()};11={bpa.neworderid()};54=1;55=FB;38=100;44=150;167=FUT"
        result = baripool.on_new_order(buy_order_fix)
        # result should have 150=8
        self.assertTrue(result.find("150=8") > 0)

    # reject options order
    def test_options_order(self):
        # Add a buy order
        buy_order_fix = f"49={random_sendercomp()};11={bpa.neworderid()};54=1;55=FB;38=100;44=150;167=OPT"
        result = baripool.on_new_order(buy_order_fix)
        # result should have 150=8
        self.assertTrue(result.find("150=8") > 0)

    # reject non-USD currency
    def test_non_usd_currency(self):
        # Add a buy order
        buy_order_fix = f"49={random_sendercomp()};11={bpa.neworderid()};54=1;55=VOD;38=100;44=150;15=BTC"
        result = baripool.on_new_order(buy_order_fix)
        # result should have 150=8
        self.assertTrue(result.find("150=8") > 0)

    # reject negative price
    def test_negative_price(self):
        # Add a buy order
        buy_order_fix = f"49={random_sendercomp()};11={bpa.neworderid()};54=1;55=VOD;38=100;44=-150"
        result = baripool.on_new_order(buy_order_fix)
        # result should have 150=8
        self.assertTrue(result.find("150=8") > 0)

    # reject negative quantity
    def test_negative_quantity(self):
        # Add a buy order
        buy_order_fix = f"49={random_sendercomp()};11={bpa.neworderid()};54=1;55=VOD;38=-100;44=150"
        result = baripool.on_new_order(buy_order_fix)
        # result should have 150=8
        self.assertTrue(result.find("150=8") > 0)

    #reject fractional quantity
    def test_fractional_quantity(self):
        # Add a buy order
        buy_order_fix = f"49={random_sendercomp()};11={bpa.neworderid()};54=1;55=VOD;38=100.5;44=150"
        result = baripool.on_new_order(buy_order_fix)
        # result should have 150=8
        self.assertTrue(result.find("150=8") > 0)

    # check lastpx
    def test_lastpx_aggressive_sell(self):
        # Add a buy order
        buy_order_fix = f"49={random_sendercomp()};11=passivebuy;54=1;55=SBUX;38=100;44=155"
        baripool.on_new_order(buy_order_fix)

        # Add a sell order
        sell_order_fix = f"49={random_sendercomp()};11=aggressivesell;54=2;55=SBUX;38=100;44=150"
        baripool.on_new_order(sell_order_fix)

        # check lastpx
        self.assertEqual(baripool.fillcontainer['passivebuy']['31'], 155)
        self.assertEqual(baripool.fillcontainer['aggressivesell']['31'], 155)

    def test_lastpx_aggressive_buy(self):
        # Add a sell order
        sell_order_fix = f"49={random_sendercomp()};11=passivesell;54=2;55=SBUX;38=100;44=154"
        baripool.on_new_order(sell_order_fix)

        # Add a buy order
        buy_order_fix = f"49={random_sendercomp()};11=aggressivebuy;54=1;55=SBUX;38=100;44=155"
        baripool.on_new_order(buy_order_fix)

        # check lastpx
        self.assertEqual(baripool.fillcontainer['passivesell']['31'], 154)
        self.assertEqual(baripool.fillcontainer['aggressivebuy']['31'], 154)

    def test_duplicate_orderid(self):
        #send 2 orders from the same client, same orderid, should reject
        buy_order_fix = "49=CarmeloAnthony;11={bpa.neworderid()};54=1;55=FB;38=100;44=150"
        baripool.on_new_order(buy_order_fix)
        result = baripool.on_new_order(buy_order_fix)
        # result should have 150=8
        self.assertTrue(result.find("Duplicate Order") > 0)
        


class TestOrderCancellation(unittest.TestCase):
    def setUp(self):
        baripool.bookshelf.clear()

    def test_cancel_order_in_book(self):
        new_order = f"8=FIX.4.2;49={random_sendercomp()};11=1234;54=1;55=AAPL;38=100;44=150.00"
        baripool.on_new_order(new_order)
        baripool.on_cancel_order("1234")
        self.assertTrue(baripool.bookshelf['AAPL'][0].is_canceled)

    #TBD
    def test_cancel_order_not_in_book(self):
        baripool.on_cancel_order("5678")
        # Test if the appropriate message is printed when the order is not found in the order book

    #TBD
    def test_cancel_order_already_canceled(self):
        new_order = f"8=FIX.4.2;49={random_sendercomp()};11=2345;54=1;55=AAPL;38=100;44=150.00"
        baripool.on_new_order(new_order)
        baripool.on_cancel_order("2345")
        baripool.on_cancel_order("2345")
        # Test if the appropriate message is printed when the order is already canceled

if __name__ == '__main__':
    unittest.main()