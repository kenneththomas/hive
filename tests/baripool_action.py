import sys
sys.path.insert(0, '../pyengine')
sys.path.insert(1, 'pyengine')
import baripool
import random as r
import uuid
import time
import yeet_test

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



bari_test()


symbols = ['AAPL', 'GOOG', 'AMZN', 'MSFT', 'TSLA']
prices = [100, 150, 200, 250, 300]

def generate_r_order():
    symbol = r.choice(symbols)
    price = r.choice(prices)
    side = r.choice(['1', '2'])

    desiredtags = f'54={side};55={symbol};38=100;44={price}'
    return yeet_test.testutils.generic_order(desiredtags=desiredtags, exported=True)

def send_r_orders(num_orders=100, sleep_interval=0.5):
    for _ in range(num_orders):
        r_order = generate_r_order()
        baripool.on_new_order(r_order)
        time.sleep(sleep_interval)

if __name__ == "__main__":
    send_r_orders()