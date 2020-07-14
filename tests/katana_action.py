import sys
sys.path.insert(0, '../pyengine')
sys.path.insert(1, 'pyengine')
import katana
import random as r
import uuid
import time

exchanges = ['NYSE','NSDQ','ARCA','BATS','EDGE','WISP']

def katana_action():
    # generate md book

    mdbook = {}
    quotes = 8

    for i in range(1,quotes):
        mdbook[str(uuid.uuid4())[0:10]] = [r.randint(1,100),r.randint(1,10) * 100,r.choice(exchanges)]

    katana.matcher('buy',r.randint(1,20) * 100,mdbook)

for i in range(0,1):
    katana_action()
    time.sleep(5)