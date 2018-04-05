import marketdata

priceawayreject = .10  #this limit checks if the price indicated on the order is a certain percentage away from market value
notionalreject = 1000000 #this limit checks if the total value of the order is greater than this limit

def limitcheck(symbol,price,quantity):

    #convert price to us penny
    pricepny = price * 100
    notionalresult = notional(price,quantity)
    if notionalresult[0] == 'Reject':
        return notionalresult
    #get market data for symbol
    marketvalue = (marketdata.getprice(symbol))
    priceawayresult = priceaway(pricepny,marketvalue)
    if priceawayresult[0] == 'Reject':
        return priceawayresult
    #if everything passes return true
    return ['Accept']

def priceaway(price,marketvalue):
    differential = marketvalue * priceawayreject
    allowedvalue = marketvalue + differential
    allowedpassivevalue = marketvalue - differential
    check = allowedvalue > price
    if allowedvalue < price:
        rejectreason = 'priceaway reject: order price deviates from market price by more than ' + str(priceawayreject)
        print(rejectreason)
        return ['Reject',rejectreason]
    elif allowedpassivevalue > price:
        rejectreason = 'priceaway reject: order price deviates from market price by more than ' + str(priceawayreject)
        print(rejectreason)
        return ['Reject',rejectreason]
    else:
        return ['Accept']

def notional(price,quantity):
    notionalvalue =  price * quantity
    if notionalvalue < notionalreject:
        return ['Accept']
    if notionalvalue > notionalreject:
        rejectreason = 'notional reject: order notional value ' + str(notionalvalue) + ' is higher than notional value limit ' + str(notionalreject)
        print(rejectreason)
        return ['Reject',rejectreason]