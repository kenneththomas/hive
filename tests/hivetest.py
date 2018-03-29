import unittest
import sys
import collections
sys.path.insert(0, '../pyengine')
sys.path.insert(1, 'pyengine')
import dumfix
import riskcheck

class dumfixtest(unittest.TestCase):
    def setUp(self):
        pass

    def test_oneplusone(self):
        self.assertEqual((1+1), 2)

    def test_fixparse(self):
        #turn a fix msg into an ordered dictionary, and confirm so
        fixmsg = '8=DUMFIX;11=4a4964c6;49=Tay;56=Spicii;35=D;55=ZVZZT;54=1;38=100;44=10;40=2;10=END'
        print('parsing fixmsg into dictionary')
        print(fixmsg)
        parsed = dumfix.parsefix(fixmsg)
        print(parsed)
        self.assertTrue('Dict' in str(type(parsed)))

    def test_exportfix(self):
        #turn an ordered dictionary into fix and confirm it generates a string
        fixdict = collections.OrderedDict({
            '8': 'DUMFIX',
            '11': 'tag11',
            '49': 'Tay',
            '56': 'Spicii',
            '35': 'D',
            '55': 'ZVZZT',
            '54': '1',
            '38': '100',
            '44': '10',
            '40': '2',
        })
        exported = dumfix.exportfix(fixdict)
        print(exported)
        self.assertTrue('str' in str(type(exported)))

class risktest(unittest.TestCase):
    def setUp(self):
        pass

    def test_oneplusone(self):
        self.assertEqual((1+1), 2)

    def test_priceaway_pass(self):
        #order price is same as market data, should accept
        check = riskcheck.priceaway(1000,1000)
        self.assertTrue(check)

    def test_priceaway_reject(self):
        #order price is way off from market data, should reject
        check = riskcheck.priceaway(5000,1000)
        self.assertFalse(check)

if __name__ == '__main__':
    unittest.main()
