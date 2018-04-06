#MOP = Market Order Pool
#Simple implementation of a Dark Pool, Market Order Pool only accepts and matches market orders.
#To begin, MOP will only accept orders of 100 quantity

import dfix
import hive
import marketdata

book = {
    'orderid1' : 'ZVZZT',
    'orderid2' : 'FB',
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
    if symbol not in book.values():
        book[orderid] = symbol
        return fix
    marketprice = marketdata.getprice(symbol)
    for matchid, matchsymbol in book.items():
        if symbol == matchsymbol:
            mopfill(fix,marketprice)
            del book[matchid]
            return fix

def mopfill(fix,fillprice):
    fix = dfix.tweak(fix,'150','2') #full fill
    fix = dfix.tweak(fix,'6',fillprice) # avg price
    fix = dfix.tweak(fix,'14','100') # cum qty
    fix = dfix.tweak(fix,'151','0') # leaves qty
    return fix

