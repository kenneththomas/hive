import marketdata

#this limit checks if the price indicated on the order is a certain percentage away from market value
priceawayreject = .10
notionalreject = 1000000

def limitcheck(symbol,price,quantity):
    #if ANY rejects, function returns false

    #convert price to us penny
    pricepny = price * 100
    if not notional(price,quantity): #should we be consistent using price and price in pennies? probably.
        return False
    #get market data for symbol
    marketvalue = (marketdata.getprice(symbol))
    if not priceaway(pricepny,marketvalue):
        return False
    #if everything passes return true
    return True





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
        print('notional reject: order notional value ' + str(notionalvalue) + ' is higher than notional value limit ' + str(notionalreject))
        return False
