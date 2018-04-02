import unittest
import sys
import collections
sys.path.insert(0, '../pyengine')
sys.path.insert(1, 'pyengine')
import dfix
import riskcheck
import hive

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

class dfixtest(unittest.TestCase):
    def setUp(self):
        pass

    def test_fixparse(self):
        #turn a fix msg into an ordered dictionary, and confirm so
        fixmsg = '8=DFIX;11=4a4964c6;49=Tay;56=Spicii;35=D;55=ZVZZT;54=1;38=100;44=10;40=2;10=END'
        parsed = dfix.parsefix(regfix)
        self.assertTrue('Dict' in str(type(parsed)))

    def test_exportfix(self):
        #turn an ordered dictionary into fix and confirm it generates a string

        exported = dfix.exportfix(fixdict)
        self.assertTrue('str' in str(type(exported)))

    def test_subscription_true(self):
        #send 40=2 and check if 40 == 2, should return true
        sub = dfix.subscription(fixdict,'40','2')
        self.assertTrue(sub)

    def test_subscription_false(self):
        #send 40=2 and check if 40 == 1, should return false
        sub = dfix.subscription(fixdict,'40','1')
        self.assertFalse(sub)

    def test_tweak(self):
        #change 40=2 to 40=1
        newfix = dfix.tweak(fixdict,'40','1')
        self.assertEqual(newfix.get('40'),'1')

    def test_tweak_newtag(self):
        #tweak should be able to add a brand new tag
        newfix = dfix.tweak(fixdict,'3001','VWAP')
        self.assertEqual(newfix.get('3001'),'VWAP')

    def test_subtweak_match(self):
        #tweak fix based on subscription
        newfix = fixdict
        if dfix.subscription(fixdict,'40','2'):
            newfix = dfix.tweak(fixdict,'40','3')
        self.assertEqual(newfix.get('40'),'3')

    def test_subtweak_nomatch(self):
        #dont tweak fix cuz it doesn't match
        newfix = fixdict
        if dfix.subscription(fixdict,'40','1'):
            newfix = dfix.tweak(fixdict,'40','3')
        self.assertEqual(newfix.get('40'),'3')

    def test_movetoend(self):
        newfix = dfix.trailer(tne)
        #convert fix
        listversion = (list(newfix.items()))
        lasttag = [('10', 'END')]
        self.assertEqual(listversion[-1],lasttag[0])


class risktest(unittest.TestCase):
    def setUp(self):
        pass

    def test_priceaway_pass(self):
        #order price is same as market data, should accept
        check = riskcheck.priceaway(1000,1000)
        self.assertTrue(check)

    def test_aggpriceaway_reject(self):
        #order price is too aggressive compared to market data, should reject
        check = riskcheck.priceaway(5000,1000)
        self.assertFalse(check)

    def test_passivepriceaway_reject(self):
        #order price is too passive compared to market data, should reject
        check = riskcheck.priceaway(800,1000)
        self.assertFalse(check)

    def test_notional_pass(self):
        #order value is less than notional limit
        check = riskcheck.notional(100,100)
        self.assertTrue(check)

    def test_notional_reject(self):
        #order value is more than notional limit
        check = riskcheck.notional(100,20000)
        self.assertFalse(check)

class gatewaytest(unittest.TestCase):
    def setUp(self):
        pass

    def test_35val_rejectv2(self):
        #tag 35=D/G/F are valid values of tag 35
        check = hive.fixvalidator(['D','G','F'],'V')
        self.assertFalse(check)

    def test_35val_acceptv2(self):
        #tag 35=D/G/F are valid values of tag 35
        check = hive.fixvalidator(['D','G','F'],'G')
        self.assertTrue(check)

class f2btest(unittest.TestCase):
    def setUp(self):
        pass

    def test_getresponse(self):
        #get an exec report from hive by sending through fix gateway
        execreport = hive.fixgateway(regfix)
        self.assertTrue('35=8;' in execreport)

    def test_reject(self):
        #get reject (for now from notional value check)
        fix = '8=DFIX;11=4a4964c6;49=Tay;56=Spicii;35=D;55=ZVZZT;54=1;38=10000;44=10000;40=2;10=END'
        execreport = hive.fixgateway(fix)
        self.assertTrue('150=8;' in execreport)

    def test_ack(self):
        #order passes limit checks and we get new order
        fix = '8=DFIX;11=4a4964c6;49=Tay;56=Spicii;35=D;55=ZVZZT;54=1;38=100;44=10;40=2;10=END'
        execreport = hive.fixgateway(fix)
        self.assertTrue('150=0;' in execreport)

    def test_invalid35(self):
        fix = '8=DFIX;11=4a4964c6;49=Tay;56=Spicii;35=V;55=ZVZZT;54=1;38=100;44=10;40=2;10=END'
        execreport = hive.fixgateway(fix)
        self.assertTrue('150=8;' in execreport)

    def test_tailer(self):
        fix = '8=DFIX;11=4a4964c6;49=Tay;56=Spicii;35=V;55=ZVZZT;54=1;38=100;44=10;40=2;10=END'
        execreport = hive.fixgateway(fix)
        #convert back into dictionary
        tailerdict = dfix.parsefix(execreport)
        #convert dictionary to list so we can check order
        listtailer = list(tailerdict)
        self.assertEqual(listtailer[-1],'10')

    def tearDown(self):
        pass

class fillsimtest(unittest.TestCase):
    def setUp(self):
        pass

    def test_fillsim100(self):
        #100 qty order should be filled if market value is good
        result3 = hive.fillsimulate(fixdict)
        self.assertEqual(result3.get('150'),'2')

    def test_fillsim200(self):
        #200 qty order should be partially filled for 100 if market value is good
        fixdict2 = fixdict
        dfix.tweak(fixdict2,'38','200')
        result = hive.fillsimulate(fixdict2)
        self.assertEqual(result.get('150'),'1')


if __name__ == '__main__':
    unittest.main()
