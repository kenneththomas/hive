#MOP = Market Order Pool
#Simple implementation of a Dark Pool, Market Order Pool only accepts and matches market orders.
#To begin, MOP will only accept orders of 100 quantity

import dfix
import hive
import marketdata

buybook = {
    'orderid1' : 'ZVZZT',
    'orderid2' : 'FB',
}

sellbook = {
    'orderid3' : 'GE',
    'orderid4' : 'ZNGA',
}

def mopvalidator(ordertype,orderqty): # validates mop can support order
    if ordertype != '1':
        return False
    elif orderqty != '100': #temporary
        return False
    else:
        return True

def mop(fix):
    ordertype = fix.get('40')
    orderqty = fix.get('38')
    if not mopvalidator(ordertype,orderqty):
        fix = hive.rejectorder(fix,'MOP only supports 100 QTY Market Orders')
        return fix
    symbol = fix.get('55')
    orderid = fix.get('11')
    side = fix.get('54')
    marketprice = marketdata.getprice(symbol) / 100
    print(marketprice)
    if side == '1': # buy order
        if symbol not in sellbook.values():
            buybook[orderid] = symbol
            fix = dfix.tweak(fix,'150','0')
            return fix
        for matchid, matchsymbol in sellbook.items():
            if symbol == matchsymbol:
                mopfill(fix,marketprice)
                del sellbook[matchid]
                return fix
    if side == '2': # sell order
        if symbol not in buybook.values():
            sellbook[orderid] = symbol
            fix = dfix.tweak(fix, '150', '0')
            return fix
        for matchid, matchsymbol in buybook.items():
            if symbol == matchsymbol:
                mopfill(fix,marketprice)
                del buybook[matchid]
                return fix

def mopfill(fix,fillprice):
    fix = dfix.tweak(fix,'150','2') #full fill
    fix = dfix.tweak(fix,'6',str(fillprice)) # avg price
    fix = dfix.tweak(fix,'14','100') # cum qty
    fix = dfix.tweak(fix,'151','0') # leaves qty
    return fix

