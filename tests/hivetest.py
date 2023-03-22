import unittest
import sys
import collections
sys.path.insert(0, '../pyengine')
sys.path.insert(1, 'pyengine')
import dfix
import katana
import rain

#reuse this one fixdict
fixdict = collections.OrderedDict({
    '8': 'DFIX',
    '11': 'tag11',
    '49': 'Tay',
    '56': 'Spicii',
    '35': 'D',
    '55': 'ZVZZT',
    '54': '1',
    '38': '100',
    '44': '10',
    '40': '2',
    '10': 'END',
})

tne = collections.OrderedDict({
    '8' : 'DIFX',
    '10': 'END',
    '55': 'ZVZZT',
})

#reuse this too
regfix = '8=DFIX;11=4a4964c6;49=Tay;56=Spicii;35=D;55=ZVZZT;54=1;38=100;44=10;40=2;10=END'



class katanatest(unittest.TestCase):
    def setUp(self):
        pass

    def test_buy_match(self):

        # given the below book, we should use the quotes in this order - A,C,D,B
        book1 = {
            'A' : [10.00,100,'NYSE'],
            'B' : [10.05,500,'NSDQ'],
            'C' : [10.03,300,'BATS'],
            'D' : [10.03,100,'NYSE'],
        }
        slices = katana.matcher('buy',1000,book1)

        # get quoteids
        q1 = dfix.parsefix(slices[0])['11']
        q2 = dfix.parsefix(slices[1])['11']
        q3 = dfix.parsefix(slices[2])['11']
        q4 = dfix.parsefix(slices[3])['11']

        self.assertEqual(q1 + q2 + q3 + q4,'ACDB')

    def test_sell_match(self):

        # given the below book, we should use the quotes in this order - B,C,A,D
        book1 = {
            'A' : [10.00,200,'NYSE'],
            'B' : [10.05,400,'NSDQ'],
            'C' : [10.03,300,'BATS'],
            'D' : [10.00,100,'NSDQ'],
        }
        slices = katana.matcher('sell',1000,book1)

        # get quoteids
        q1 = dfix.parsefix(slices[0])['11']
        q2 = dfix.parsefix(slices[1])['11']
        q3 = dfix.parsefix(slices[2])['11']
        q4 = dfix.parsefix(slices[3])['11']

        self.assertEqual(q1 + q2 + q3 + q4,'BCAD')

    def test_limitprice_buy(self):

        # given the below book, a limit price of 10.01 should eliminate quotes B and C

        book2 = {
            'A' : [10.00,100,'NYSE'],
            'B' : [10.05,600,'NSDQ'],
            'C' : [10.03,300,'BATS'],
            'D' : [10.01,100,'BATS'],
        }

        limitprice = 10.01
        remainingbook = katana.quotetrimmer('buy',limitprice,book2)

        limittestpass = True
        for quote in remainingbook.keys():
            if remainingbook[quote][0] > limitprice:
                limittestpass=False

        self.assertTrue(limittestpass)

    def test_limitprice_sell(self):

        # given the below book, a limit price of 10.02 should eliminate quotes A and D

        book2 = {
            'A': [10.00, 100, 'NYSE'],
            'B': [10.05, 600, 'NSDQ'],
            'C': [10.03, 300, 'BATS'],
            'D': [10.01, 100, 'BATS'],
        }

        limitprice = 10.02
        remainingbook = katana.quotetrimmer('sell', limitprice, book2)

        limittestpass = True
        for quote in remainingbook.keys():
            if remainingbook[quote][0] < limitprice:
                limittestpass = False

        self.assertTrue(limittestpass)

    def test_directed(self):

        # given the below book and a directed order for BATS we would only use quotes C and D

        book2 = {
            'A' : [10.00,100,'NYSE'],
            'B' : [10.05,600,'NSDQ'],
            'C' : [10.03,300,'BATS'],
            'D' : [10.01, 100, 'BATS'],
        }
        directvenue = 'BATS'
        remainingbook = katana.directedtrimmer(directvenue,book2)

        directtestpass = True
        for quote in remainingbook.keys():
            if remainingbook[quote][2] != directvenue:
                directtestpass=False

        self.assertTrue(directtestpass)

class raintest(unittest.TestCase):
    def setUp(self):
        rain.schema = rain.parse_schema('tests/resources/rain_schema.json')
        pass

    def test_maxqty_defined_pass(self):
        check = rain.process_order('kenneth', 100)
        self.assertTrue(check)

    def test_maxqty_defined_reject(self):
        check = rain.process_order('kenneth', 1001)
        self.assertFalse(check)

    def test_maxqty_default_pass(self):
        check = rain.process_order('benneth', 99)
        self.assertTrue(check)

    def test_maxqty_default_reject(self):
        check = rain.process_order('benneth', 101)
        self.assertFalse(check)

if __name__ == '__main__':
    unittest.main()
