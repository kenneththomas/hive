import unittest
import sys
import collections
sys.path.insert(0, '../pyengine')
sys.path.insert(1, 'pyengine')
import dumfix
import riskcheck
import hive

#reuse this one fixdict
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
    '10': 'END',
})

tne = collections.OrderedDict({
    '8' : 'DUMFIX',
    '10': 'END',
    '55': 'ZVZZT',
})

#reuse this too
regfix = '8=DUMFIX;11=4a4964c6;49=Tay;56=Spicii;35=D;55=ZVZZT;54=1;38=100;44=10;40=2;10=END'

class dumfixtest(unittest.TestCase):
    def setUp(self):
        pass

    def test_fixparse(self):
        #turn a fix msg into an ordered dictionary, and confirm so
        fixmsg = '8=DUMFIX;11=4a4964c6;49=Tay;56=Spicii;35=D;55=ZVZZT;54=1;38=100;44=10;40=2;10=END'
        print('parsing fixmsg into dictionary')
        print(regfix)
        parsed = dumfix.parsefix(regfix)
        print(parsed)
        self.assertTrue('Dict' in str(type(parsed)))

    def test_exportfix(self):
        #turn an ordered dictionary into fix and confirm it generates a string

        exported = dumfix.exportfix(fixdict)
        print(exported)
        self.assertTrue('str' in str(type(exported)))

    def test_subscription_true(self):
        #send 40=2 and check if 40 == 2, should return true
        sub = dumfix.subscription(fixdict,'40','2')
        self.assertTrue(sub)

    def test_subscription_false(self):
        #send 40=2 and check if 40 == 1, should return false
        sub = dumfix.subscription(fixdict,'40','1')
        self.assertFalse(sub)

    def test_tweak(self):
        #change 40=2 to 40=1
        newfix = dumfix.tweak(fixdict,'40','1')
        self.assertEqual(newfix.get('40'),'1')

    def test_tweak_newtag(self):
        #tweak should be able to add a brand new tag
        newfix = dumfix.tweak(fixdict,'3001','VWAP')
        self.assertEqual(newfix.get('3001'),'VWAP')

    def test_subtweak_match(self):
        #tweak fix based on subscription
        newfix = fixdict
        if dumfix.subscription(fixdict,'40','2'):
            newfix = dumfix.tweak(fixdict,'40','3')
        self.assertEqual(newfix.get('40'),'3')

    def test_subtweak_nomatch(self):
        #dont tweak fix cuz it doesn't match
        newfix = fixdict
        if dumfix.subscription(fixdict,'40','1'):
            newfix = dumfix.tweak(fixdict,'40','3')
        self.assertEqual(newfix.get('40'),'3')

    def test_movetoend(self):
        newfix = dumfix.trailer(tne)
        print(newfix)
        #convert fix
        listversion = (list(newfix.items()))
        print(listversion)
        print(listversion[-1])
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

    def test_35val_pass(self): #currently unused
        #tag 35=D/G/F are valid values of tag 35
        check = hive.messagetypevalidation('D')
        self.assertTrue(check)

    def test_35val_reject(self): #currently unused
        #tag 35=D/G/F are valid values of tag 35
        check = hive.messagetypevalidation('V')
        self.assertFalse(check)

    def test_35val_rejectv2(self):
        #tag 35=D/G/F are valid values of tag 35
        check = hive.fixvalidator(['D','G','F'],'V')
        self.assertFalse(check)

    def test_35val_acceptv2(self):
        #tag 35=D/G/F are valid values of tag 35
        check = hive.fixvalidator(['D','G','F'],'G')
        print(check)
        self.assertTrue(check)

class f2btest(unittest.TestCase):
    def setUp(self):
        pass

    def test_getresponse(self):
        #get an exec report from hive by sending through fix gateway
        execreport = hive.fixgateway(regfix)
        print(execreport)
        self.assertTrue('35=8;' in execreport)

    def test_reject(self):
        #get reject (for now from notional value check)
        fix = '8=DUMFIX;11=4a4964c6;49=Tay;56=Spicii;35=D;55=ZVZZT;54=1;38=10000;44=10000;40=2;10=END'
        execreport = hive.fixgateway(fix)
        self.assertTrue('150=8;' in execreport)

    def test_ack(self):
        #order passes limit checks and we get new order
        fix = '8=DUMFIX;11=4a4964c6;49=Tay;56=Spicii;35=D;55=ZVZZT;54=1;38=100;44=10;40=2;10=END'
        execreport = hive.fixgateway(fix)
        self.assertTrue('150=0;' in execreport)

    def test_invalid35(self):
        fix = '8=DUMFIX;11=4a4964c6;49=Tay;56=Spicii;35=V;55=ZVZZT;54=1;38=100;44=10;40=2;10=END'
        execreport = hive.fixgateway(fix)
        self.assertTrue('150=8;' in execreport)

    def test_tailer(self):
        fix = '8=DUMFIX;11=4a4964c6;49=Tay;56=Spicii;35=V;55=ZVZZT;54=1;38=100;44=10;40=2;10=END'
        execreport = hive.fixgateway(fix)
        #convert back into dictionary
        tailerdict = dumfix.parsefix(execreport)
        #convert dictionary to list so we can check order
        listtailer = list(tailerdict)
        print(listtailer)
        self.assertEqual(listtailer[-1],'10')

    def tearDown(self):
        pass

class fillsimtest(unittest.TestCase):
    def setUp(self):
        pass

    def test_fillsim100(self):
        #100 qty order should be filled if market value is good
        result3 = hive.fillsimulate(fixdict)
        print(result3)
        self.assertEqual(result3.get('150'),'2')

    def test_fillsim200(self):
        #200 qty order should be partially filled for 100 if market value is good
        fixdict2 = fixdict
        dumfix.tweak(fixdict2,'38','200')
        print(fixdict2)
        result = hive.fillsimulate(fixdict2)
        print(result)
        print(result.get('150'))
        self.assertEqual(result.get('150'),'1')


if __name__ == '__main__':
    unittest.main()
