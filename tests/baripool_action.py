import sys
sys.path.insert(0, '../pyengine')
sys.path.insert(1, 'pyengine')
import baripool
import random as r
import uuid
import time

def neworderid():
    return 'katana-' + str(uuid.uuid4())[0:8]

def bari_test():
    print('bari test')
    
    order1 = '35=D;11={};54=1;55=ZVZZT;40=2;38=100;44=9.98'.format(neworderid())
    order2 = '35=D;11={};54=2;55=ZVZZT;40=2;38=100;44=10.02'.format(neworderid())
    order3 = '35=D;11={};54=1;55=ZVZZT;40=2;38=100;44=10.01'.format(neworderid())
    order4 = '35=D;11={};54=2;55=ZVZZT;40=2;38=100;44=10.01'.format(neworderid())

    baripool.on_new_order(order1)
    baripool.on_new_order(order2)
    baripool.on_new_order(order3)
    baripool.on_new_order(order4)

def bari_test2():
    print('bari test 2')
    
    for x in range(10):
        order = '35=D;11={};54={};55=ZVZZT;40=2;38=100;44={}.{}'.format(neworderid(),r.randint(1,2),r.randint(8,11),r.randint(0,99))
        #time.sleep(2)
        baripool.on_new_order(order)

bari_test()
#bari_test2()