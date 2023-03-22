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
prices = [100, 150, 200, 250, 300]

def generate_r_order():
    symbol = r.choice(symbols)
    price = r.choice(prices)
    side = r.choice(['1', '2'])

    desiredtags = f'54={side};55={symbol};38=100;44={price};49={r.choice(sendercompids)}'
    return yeet_test.testutils.generic_order(desiredtags=desiredtags, exported=True)

def send_r_orders(num_orders=100, sleep_interval=1):
    for _ in range(num_orders):
        r_order = generate_r_order()
        baripool.on_new_order(r_order)
        time.sleep(sleep_interval)

if __name__ == "__main__":
    send_r_orders()