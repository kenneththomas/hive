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

class testutils():
    def generic_order(desiredtags='8=FIX.4.2',exported=False):
        tags = collections.OrderedDict()

        tags['8'] = 'FIX.4.2'
        tags['35'] = 'D'
        tags['49'] = 'YEET_DEV'
        tags['56'] = 'YEET2'
        #set tag 11 to 10 digit uuid
        tags['11'] = str(uuid.uuid4())[:10]
        #set tag 52 to timestamp
        tags['52'] = datetime.datetime.now().strftime('%Y%m%d-%H:%M:%S.%f')[:-3]
        #tags['1'] = 'TEST_ACCOUNT'
        tags['54'] = '1'
        tags['55'] = 'ZVZZT'
        tags['40'] = '2'
        tags['38'] = '100'
        tags['44'] = '10.00'
        tags['10'] = '000'

        #parse desiredtags and apply them
        parsed = dfix.parsefix(desiredtags)
        for tag in parsed.keys():
            tags[tag] = parsed[tag]

        if exported:
            return dfix.exportfix(tags)
        else:
            return tags

    def validator(output, expected, parsed=True):
        if not parsed:
            output = dfix.parsefix(output)
        expected = dfix.parsefix(expected)
        for tag in expected.keys():
            if tag not in output.keys():
                return False
            if output[tag] != expected[tag]:
                return False
        return True

class TestYeet(unittest.TestCase):

    def test_parse_failure(self):
        parse_failure_result = yeet.parse_new_msg('notafixmsg')
        self.assertFalse(parse_failure_result)

    def test_unknown_sendercomp(self):
        unknown_sendercomp_result = yeet.parse_new_msg(testutils.generic_order('49=rahul.ligma@twitter.com;56=gerg;',True))
        self.assertTrue(testutils.validator(unknown_sendercomp_result, '150=8;',False))
    
    def test_unknown_targetcomp(self):
        unknown_targetcomp_result = yeet.parse_new_msg(testutils.generic_order('49=YEET_DEV;56=nottherightthing;',True))
        self.assertTrue(testutils.validator(unknown_targetcomp_result, '150=8;',False))

    def test_working_order(self):
        working_order_result = yeet.parse_new_msg(testutils.generic_order(exported=True))
        self.assertTrue(testutils.validator(working_order_result, '150=0;',False))

    def test_working_fill(self):
        order1 = yeet.parse_new_msg(testutils.generic_order(exported=True))
        order2 = yeet.parse_new_msg(testutils.generic_order('49=BROADCAP;56=YEET;11=1234567890;54=2;38=100;',exported=True))
        # right now it only returns acks but we want to check for a fill eventually
        self.assertTrue(testutils.validator(order1, '150=0;',False))

class TestClientMgr(unittest.TestCase):
    def test_account_not_found(self):
        #derive clientid but have account not valid for clientid
        account_not_found_result = yeet.client_manager(testutils.generic_order('1=baris bank account;'))
        self.assertTrue(testutils.validator(account_not_found_result, '150=8;109=NO CAP;'))

    def  test_use_default_account(self):
        #send no value of tag 1 and confirm default account is used
        use_default_account_result = yeet.client_manager(testutils.generic_order())
        self.assertTrue(testutils.validator(use_default_account_result, '1=GINGERBREAD;'))
    

if __name__ == '__main__':
    unittest.main()