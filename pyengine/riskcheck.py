import marketdata

#this limit checks if the price indicated on the order is a certain percentage away from market value
priceawayreject = .10
notionalreject = 1000000

def limitcheck(symbol,price,quantity):
    #convert price to us penny
    pricepny = price * 100
    #get market data for symbol
    marketvalue = (marketdata.getprice(symbol))
    priceaway(pricepny,marketvalue)
    notional(price,quantity)

#starts with aggressive only

def priceaway(price,marketvalue):
    print('priceaway check' + ' price: ' + str(price) + ' market value: ' + str(marketvalue))
    differential = marketvalue * priceawayreject
    allowedvalue = marketvalue + differential
    allowedpassivevalue = marketvalue - differential
    check = allowedvalue > price
    if allowedvalue < price:
        print('priceaway reject: order price deviates from market price by more than ' + str(priceawayreject))
        return False
    elif allowedpassivevalue > price:
        print('priceaway reject: order price deviates from market price by more than ' + str(priceawayreject))
        return False
    else:
        return True

def notional(price,quantity):
    notionalvalue =  price * quantity
    if notionalvalue < notionalreject:
        return True
    if notionalvalue > notionalreject:
        print('notional reject: order notional value is higher than notional value limit')
        return False
