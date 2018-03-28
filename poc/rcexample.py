#checking out risk checks
import sys
import time
sys.path.insert(0, '../pyengine')

import riskcheck
import marketdata

def s(t):
  time.sleep(t)

s(1.5)
print('poc: let\'s try out the priceaway check. first, let\'s get one rejected')
s(1.5)
riskcheck.limitcheck('ZVZZT',12)
s(1.5)
print('poc: now let\'s do the same symbol, but with a closer price to market')
s(1.5)
riskcheck.limitcheck('ZVZZT',10.54)
s(1.5)
print('notice this order was not rejected')
