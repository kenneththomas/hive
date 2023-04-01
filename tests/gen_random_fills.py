import pnltest
import sys
import collections
import random
import uuid
sys.path.insert(0, '../pyengine')
sys.path.insert(1, 'pyengine')
import dfix

#create ordereddict with only tag 8


exchanges = ['NYSE','NSDQ','BATS','BARI','AMEX','PHLX','BOSX','MIAX','CMEX','CBOE','ICEX']
tradernames = ['Devon Achane','Ainias Smith','Connor Weigman','Kenna Bates','Opal Press','Dashawn Miller']
companies = ['']

def emailgen(fullname=random.choice(tradernames)):
    return fullname.lower().replace(' ','.') + '@yeet.com'


def exchangeselector(exchlist=exchanges):
    return random.choice(exchlist)

def multifill(fills,desiredtagspf='8=FIX.4.2'):
    fillcontainer = []
    tag37 = str(uuid.uuid4())[:20]
    tag11 = str(uuid.uuid4())[:10]
    #get only letters and numbers in tag37
    tag37 = ''.join(e for e in tag37 if e.isalnum())
    trader = random.choice(tradernames)
    tag50 =  trader
    tag1 = emailgen(trader)

    clienttags = f'1={tag1};50={tag50};'

    for i in range(0,fills-1):
        tag17= str(uuid.uuid4())[:15]
        exch = exchangeselector()
        fill = pnltest.testutils.genericfill(clienttags + f'11={tag11};37={tag37};17={tag17};150=1;39=1;76={exch};',True)
        print(fill)
        fillcontainer.append(fill)
    
    #final fill
    tag17= str(uuid.uuid4())[:15]
    fill = pnltest.testutils.genericfill(clienttags + f'11={tag11};37={tag37};17={tag17};150=2;39=2',True)
    print(fill)
    fillcontainer.append(fill)


    return fills

multifill(5)