import sys
sys.path.insert(0, '../pyengine')
sys.path.insert(1, 'pyengine')
sys.path.insert(1, 'tests/resources')
import baripool
import random as r
import uuid
import time
import yeet_test
import devresources

sendercompids = list(devresources.clients.keys())

def neworderid():
    return 'katana-' + str(uuid.uuid4())[0:8]

symbols = ['AAPL', 'GOOG', 'AMZN', 'MSFT', 'TSLA', 'MS', 'BAC', 'ZVZZT', 'SPY', 'QQQ','IWM','META','GME','AMC','BB','NOK','V','EL','LULU']

#generate random price, use cents
prices = [str(r.randint(1, 1000)) + '.' + str(r.randint(10, 99)) for _ in range(100)]

def generate_r_order():
    symbol = r.choice(symbols)
    price = r.choice(prices)
    side = r.choice(['1', '2'])
    #generate random quantity for order
    qty = str(r.randint(1, 1000))

    desiredtags = f'54={side};55={symbol};38={qty};44={price};49={r.choice(sendercompids)}'
    return yeet_test.testutils.generic_order(desiredtags=desiredtags, exported=True)

def send_r_orders(num_orders=10000, sleep_interval=.5):

    #count orders already sent
    order_count = 0
    for _ in range(num_orders):
        r_order = generate_r_order()
        baripool.on_new_order(r_order)
        order_count += 1

        # after 50 orders sent, slow sleep interval to random between 5 and 14 seconds
        if order_count % 50 == 0:
            sleep_interval = r.randint(5, 14)
            print(f'Orders sent: {order_count}, resting for {sleep_interval} seconds')

        time.sleep(sleep_interval)

#for bp_directentry population
def bp_directentry_sim(num_orders=6, sleep_interval=0):
    for _ in range(num_orders):
        r_order = generate_r_order()
        baripool.on_new_order(r_order)

if __name__ == "__main__":
    send_r_orders()