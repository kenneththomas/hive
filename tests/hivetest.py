import unittest
import sys
import collections
sys.path.insert(0, '../pyengine')
sys.path.insert(1, 'pyengine')
import dfix
import riskcheck
import hive
import mop
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

    def test_strip(self):
        badfix = '8=DFIX;35=D;55=GE;10=END;' #trails with delimiter, our parser doesn't like this
        betterfix = dfix.dfixformat(badfix)
        self.assertEqual(betterfix, '8=DFIX;35=D;55=GE;10=END') # format should return same message but with no semicolon at end

    def test_multitweak(self):
        oldfix = collections.OrderedDict({
            '8': 'DFIX',
            '10': 'END',
            '55': 'ZVZZT',
            '40': '2',
        })
        newfix = dfix.multitweak(oldfix,'40=1;8=DFIX')
        self.assertTrue(newfix.get('40') == '1' and newfix.get('8') == 'DFIX')

    def test_newfix(self):
        sample = '35=D;49=SENDER;56=RECEIVER;11=orderid;'
        a = dfix.fix(sample)
        print(a.msgtype)


class risktest(unittest.TestCase):
    def setUp(self):
        pass

    def test_priceaway_pass(self):
        #order price is same as market data, should accept
        check = riskcheck.priceaway(1000,1000)
        self.assertTrue(check[0] == 'Accept')

    def test_aggpriceaway_reject(self):
        #order price is too aggressive compared to market data, should reject
        check = riskcheck.priceaway(5000,1000)
        self.assertTrue(check[0] == 'Reject')

    def test_passivepriceaway_reject(self):
        #order price is too passive compared to market data, should reject
        check = riskcheck.priceaway(800,1000)
        self.assertTrue(check[0] == 'Reject')

    def test_notional_accept(self):
        #order value is less than notional limit
        check = riskcheck.notional(100,100)
        self.assertTrue(check[0] == 'Accept')

    def test_notional_reject(self):
        #order value is more than notional limit
        check = riskcheck.notional(100,20000)
        self.assertTrue(check[0] == 'Reject')

    def test_suspended_accept(self):  # maybe unneccessary
        #symbol is not suspended
        check = riskcheck.suspendedcheck('ZVZZT')
        self.assertTrue(check)

    def test_suspended_reject(self):  # maybe unnecessary
        check = riskcheck.suspendedcheck('SPOT')
        self.assertFalse(check)

    def test_suspendadd_reject(self):
        riskcheck.suspendsymbol('TEST')
        check = riskcheck.suspendedcheck('TEST')
        self.assertFalse(check)

    def test_unsuspend_accept(self):
        riskcheck.unsuspendsymbol('TEST')
        check = riskcheck.suspendedcheck('TEST')
        self.assertTrue(check)

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

    def test_appendreject(self):
        #test appending reject message
        fix = '8=DFIX;11=4a4964c6;49=Tay;56=Spicii;35=D;55=ZVZZT;54=1;38=10000;44=10000;40=2;10=END'
        check = hive.rejectorder(dfix.parsefix(fix),'test reject')
        self.assertEqual(check.get('58'),'test reject')

class f2btest(unittest.TestCase):
    def setUp(self):
        pass

    def test_getresponse(self):
        #get an exec report from hive by sending through fix gateway
        execreport = hive.fixgateway(regfix)
        self.assertTrue('35=8;' in execreport)

    def test_notionalvalue_reject(self):
        #get reject from notional limit check
        fix = '8=DFIX;11=4aasd6sdf6;49=Tay;56=Spicii;35=D;55=ZVZZT;54=1;38=10000;44=10000;40=2;10=END'
        execreport = hive.fixgateway(fix)
        self.assertTrue('150=8;' in execreport)

    def test_priceaway_reject(self):
        #get reject from priceaway limit check
        fix = '8=DFIX;11=4asfs4c6;49=Tay;56=Spicii;35=D;55=ZVZZT;54=1;38=100;44=9999.31;40=2;10=END'
        execreport = hive.fixgateway(fix)
        self.assertTrue('150=8;' in execreport)

    def test_ack(self):
        #order passes limit checks and we get new order
        fix = '8=DFIX;11=4a4964c6;49=Tay;56=Spicii;35=D;55=ZVZZT;54=1;38=100;40=1;10=END'
        execreport = hive.fixgateway(fix)
        self.assertTrue('150=0;' in execreport)

    def test_invalid35(self):
        fix = '8=DFIX;11=4a4asdc6;49=Tay;56=Spicii;35=V;55=ZVZZT;54=1;38=100;44=10;40=2;10=END'
        execreport = hive.fixgateway(fix)
        self.assertTrue('150=8;' in execreport)

    def test_tailer(self):
        fix = '8=DFIX;11=4a4sdf4c6;49=Tay;56=Spicii;35=V;55=ZVZZT;54=1;38=100;44=10;40=2;10=END'
        execreport = hive.fixgateway(fix)
        #convert back into dictionary
        tailerdict = dfix.parsefix(execreport)
        #convert dictionary to list so we can check order
        listtailer = list(tailerdict)
        self.assertEqual(listtailer[-1],'10')

    def test_nomarketdata(self):
        fix = '8=DFIX;35=D;11=4a4964c4;49=Tay;56=Spicii;55=NOTREALSYMBOL;54=1;38=100;44=10;40=2;10=END'
        execreport = hive.fixgateway(fix)
        self.assertTrue('market data does not exist' in execreport)

    def test_marketorderwithprice(self):
        fix = '8=DFIX;35=D;11=4a4964c7;49=Tay;56=Spicii;55=ZVZZT;54=1;38=100;44=10;40=1;10=END'
        execreport = hive.fixgateway(fix)
        self.assertTrue('Market Orders should not contain price in tag 44' in execreport)

    def test_duplicate11(self):
        #send 2 orders with same tag 11, 2nd should be rejected
        hive.tag11validation = True # this is off by default atm, so we turn it on
        fix = '8=DFIX;35=D;11=4a4964cr;49=Tay;56=Spicii;55=ZVZZT;54=1;38=100;40=1;10=END'
        hive.fixgateway(fix) #order 1
        check = hive.fixgateway(fix)
        self.assertTrue('Duplicate value of tag 11 is not allowed' in check)

    def test_hundoslicer_fill(self):
        #submit buy order of 300, submit sell order of 300, fills in hundoslicer
        fix1 = '8=DFIX;35=D;11=hs1;49=Tay;56=Spicii;55=MS;54=1;38=300;40=1;10=END'
        fix2 = '8=DFIX;35=D;11=hs2;49=Tay;56=Spicii;55=MS;54=2;38=300;40=1;10=END'
        hive.fixgateway(fix1) # should put 3 MS buy in MOP book
        check = hive.fixgateway(fix2) # should fill with above order
        self.assertTrue('150=2' in check)

    def test_currency_reject(self):
        fix = '8=DFIX;35=D;11=4a4sdfc4;49=Tay;56=Spicii;55=ZVZZT;15=HKD;54=1;38=100;44=10;40=2;10=END'
        check = hive.fixgateway(fix)
        self.assertTrue('Unsupported Currency' in check)

    def test_currency_convert(self):
        fix = '8=DFIX;35=D;11=4a4awb;49=Tay;56=Spicii;55=ZVZZT;15=CAD;54=1;38=100;44=10;40=2;10=END'
        check = hive.fixgateway(fix)
        self.assertTrue('15=USD' in check)

    def test_mutombo(self):
        fix = '8=DFIX;35=D;11=4a4awb;49=Tay;56=Spicii;55=ZVZZT;57=MATU;54=1;38=100;44=10;40=2;10=END'
        check = hive.fixgateway(fix)
        self.assertTrue('150=8' in check)

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

class marketorderpooltest(unittest.TestCase):
    def test_2orders_1match(self):
        #send 2 orders, 1st one does not get filled and second one does
        fix1 = '8=DFIX;35=D;11=4a4964c6;49=Tay;56=Spicii;55=TWTR;54=1;38=100;40=1;10=END'
        fix2 = '8=DFIX;35=D;11=4a4964c6;49=Tay;56=Spicii;55=TWTR;54=2;38=100;40=1;10=END'
        fix1 = dfix.parsefix(fix1)
        fix2 = dfix.parsefix(fix2)
        mop.mop(fix1)
        check = mop.mop(fix2)
        self.assertEqual(check.get('150'),'2')

    def test_reject_non100(self):
        fix1 = '8=DFIX;35=D;11=4a4964c6;49=Tay;56=Spicii;55=NOTREALSYMBOL;54=1;38=200;40=1;10=END'
        fix1 = dfix.parsefix(fix1)
        check = mop.mop(fix1)
        self.assertEqual(check.get('150'),'8')

    def test_reject_limitorder(self):
        fix1 = '8=DFIX;35=D;11=4a4964c6;49=Tay;56=Spicii;55=NOTREALSYMBOL;54=1;38=100;44=10;40=2;10=END'
        fix1 = dfix.parsefix(fix1)
        check = mop.mop(fix1)
        self.assertEqual(check.get('150'),'8')

class algotest(unittest.TestCase):

    def test_hundoslice(self):
        #order of 300 should create 3 slices into MOP
        fix1 = '8=DFIX;35=D;11=4a49s4c6;49=Tay;56=Spicii;55=TWTR;54=1;38=300;40=1;10=END'
        fix1 = dfix.parsefix(fix1)
        check = hive.hundoslice(fix1)
        c = collections.Counter(mop.buybook.values()) # this thing counts how many of each value
        #c['TWTR'] this is how we check how many times twitter appears
        self.assertEqual(c['TWTR'],3) #as order was 300, there should be 3 slices

    def test_hundoslice_qty_150(self):
        fix1 = '8=DFIX;35=D;11=4a49s4c6;49=Tay;56=Spicii;55=TWTR;54=1;38=150;40=1;10=END'
        fix1 = dfix.parsefix(fix1)
        check = hive.hundoslice(fix1)
        self.assertEqual(check.get('58'),'hundoslice reject: order not divisible by 100')

class admintest(unittest.TestCase):

    def test_blockfix(self):
        fix1 = '8=DFIX;35=UAC;57=fixserver;58=disable fixsession;161=TBL2'
        hive.fixgateway(fix1) # run admin to disable
        fix2 = '8=DFIX;35=D;11=emafge;49=TBL2;56=Spicii;55=TWTR;54=1;38=150;40=1;10=END'
        check = hive.fixgateway(fix2)
        self.assertTrue('58=FIX Session blocked' in check)

    def test_unblockfix(self):
        fix1 = '8=DFIX;35=UAC;57=fixserver;58=enable fixsession;161=TBL2'
        hive.fixgateway(fix1) # run admin to disable
        fix2 = '8=DFIX;35=D;11=emafge2;49=TBL2;56=Spicii;55=TWTR;54=1;38=150;40=1;10=END'
        check = hive.fixgateway(fix2)
        self.assertTrue('58=FIX Session blocked' not in check)

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
        rain.schema = rain.parse_schema('resources/rain_schema.json')
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
