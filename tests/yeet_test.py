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
    def generic_order(desiredtags='8=FIX.4.2'):
        tags = collections.OrderedDict()

        tags['8'] = 'FIX.4.2'
        tags['35'] = 'D'
        tags['49'] = 'YEET_DEV'
        tags['56'] = 'YEET2'
        #set tag 11 to 10 digit uuid
        tags['11'] = str(uuid.uuid4())[:10]
        #set tag 52 to timestamp
        tags['52'] = datetime.datetime.now().strftime('%Y%m%d-%H:%M:%S.%f')[:-3]
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

        return dfix.exportfix(tags)

    def validator(output, expected):
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
        unknown_sendercomp_result = yeet.parse_new_msg(testutils.generic_order('49=rahul.ligma@twitter.com;56=gerg;'))
        self.assertTrue(testutils.validator(unknown_sendercomp_result, '150=8;'))
    
    def test_unknown_targetcomp(self):
        unknown_targetcomp_result = yeet.parse_new_msg(testutils.generic_order('49=YEET_DEV;56=nottherightthing;'))
        self.assertTrue(testutils.validator(unknown_targetcomp_result, '150=8;'))

if __name__ == '__main__':
    unittest.main()