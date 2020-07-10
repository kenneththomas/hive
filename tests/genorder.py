#used to test new features as we're building rather than to unit test
import sys
import uuid
import random

sys.path.insert(0, '../pyengine')
sys.path.insert(1, 'pyengine')
import hive
import dfix

symbols = ['AMD','FB','SNAP','ZVZZT']
sides = ['1','2','5']

def genorder():
    root = '8=FIX.4.2;35=D;49=KENNETH;56=AGORA;11=snowday-{};'.format(str(uuid.uuid4())[0:12])
    productdetails = '55={};15=USD;'.format(random.choice(symbols))
    orderdetails = '54={};40=1;38={};'.format(random.choice(sides),random.randint(1,5)*100)
    end = '10=000'

    final = root + productdetails + orderdetails + end
    print('generated order: {}'.format(final))
    return final

hive.fixgateway(genorder())