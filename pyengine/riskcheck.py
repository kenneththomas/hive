import marketdata

#this limit checks if the price indicated on the order is a certain percentage away from market value
priceawayreject = .10

def limitcheck(symbol,price):
    #convert price to us penny
    pricepny = price * 100
    #get market data for symbol
    marketvalue = (marketdata.getprice(symbol))
    priceaway(pricepny,marketvalue)

#starts with aggressive only

def priceaway(price,marketvalue):
    print('priceaway check' + ' price: ' + str(price) + ' market value: ' + str(marketvalue))
    differential = marketvalue * priceawayreject
    allowedvalue = marketvalue + differential
    check = allowedvalue > price
    if check:
        return True
    else:
        print('priceaway reject: order price deviates from market price by more than ' + str(priceawayreject))
        return False

limitcheck('ZVZZT',12)

